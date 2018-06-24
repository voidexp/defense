#include <Python.h> // must be first

#include "error.h"
#include "fs.h"
#include "memory.h"
#include "script.h"
#include <assert.h>
#include <stdarg.h>
#include <stdbool.h>
#include <string.h>

#ifdef DEBUG
# include <stdio.h>
#endif

#define INIT_FUNC_NAME "init"
#define FINI_FUNC_NAME "fini"
#define UPDATE_FUNC_NAME "update"

static const char *funcs_names[] = {
	INIT_FUNC_NAME,
	FINI_FUNC_NAME,
	UPDATE_FUNC_NAME,
};

enum {
	INIT_FUNC,
	FINI_FUNC,
	UPDATE_FUNC,
	FUNC_MAX,
};

struct ScriptData
{
	PyObject *funcs[FUNC_MAX];
};

static beer_err
call(struct BeerScript *script, int func, const char *pyarg_fmt, ...)
{
	PyObject *callable = ((struct ScriptData*)script->data_)->funcs[func];
	if (callable)
	{
		va_list vargs;
		va_start(vargs, pyarg_fmt);
		PyObject *args = Py_VaBuildValue(pyarg_fmt, vargs);
		PyObject *result = PyObject_Call(callable, args, NULL);
		Py_XDECREF(args);
		if (!result)
		{
#ifdef DEBUG
			PyErr_Print();
#endif
			return BEER_ERR_PY_EXEC;
		}
		Py_XDECREF(result);
	}
	return BEER_OK;
}

beer_err
beer_py_init(void)
{
	Py_Initialize();
	if (!Py_IsInitialized())
	{
		return BEER_ERR_PY_INIT;
	}

	PyObject *syspath = PySys_GetObject("path");
	PyObject *modpath = Py_BuildValue("s", "core/beer/python");
	PyList_Append(syspath, modpath);
	Py_DECREF(modpath);

#ifdef DEBUG
	printf("Python initialized\n");
#endif

	return BEER_OK;
}

void
beer_py_fini(void)
{
	if (Py_IsInitialized())
	{
		Py_FinalizeEx();
#ifdef DEBUG
		printf("Python finalized\n");
#endif
	}
}

beer_err
beer_script_load(const char *path, struct BeerScript **r_script)
{
	assert(path);
	assert(r_script);

	// read script file contents
	char *script = NULL;
	beer_err err = beer_file_read(path, &script, NULL);
	if (err)
	{
		return err;
	}

	PyObject *py = NULL;
	PyObject *context = NULL;
	PyObject *builtins = NULL;
	PyObject *eval = NULL;
	PyObject *funcs[FUNC_MAX] = {NULL,};

	// compile the script
	if (!(py = Py_CompileString(script, path, Py_file_input)))
	{
#ifdef DEBUG
		PyErr_Print();
#endif
		err = BEER_ERR_PY_COMPILE;
		goto error;
	}

	// prepare script execution context: create a dict which will hold the
	// globals and the locals and initialize populate its __builtins__
	context = PyDict_New();
	builtins = PyImport_ImportModule("builtins");
	PyDict_SetItemString(context, "__builtins__", builtins);
	Py_DECREF(builtins);

	// execute the script
	eval = PyEval_EvalCode(py, context, context);
	if (!eval)
	{
#ifdef DEBUG
		PyErr_Print();
#endif
		err = BEER_ERR_PY_EXEC;
		goto error;
	}

	// lookup predefined script functions
	for (int i = 0; i < FUNC_MAX; i++)
	{
		PyObject *attr = Py_BuildValue("s", funcs_names[i]);
		PyObject *func = PyObject_GetItem(context, attr);
		Py_DECREF(attr);

		if (func != NULL && !PyCallable_Check(func))
		{
			err = BEER_ERR_PY_BAD_SCRIPT;
			Py_DECREF(func);
			goto error;
		}

		funcs[i] = func;
	}

	err = beer_new(struct BeerScript, r_script);
	if (err)
	{
		goto error;
	}

	struct ScriptData *data = NULL;
	err = beer_new(struct ScriptData, &data);
	if (err)
	{
		beer_free(*r_script);
		*r_script = NULL;
		goto error;
	}

	(*r_script)->data_ = data;
	(*r_script)->path = strdup(path);
	memcpy(data->funcs, funcs, sizeof(funcs));

cleanup:
	Py_XDECREF(context);
	Py_XDECREF(eval);
	beer_free(script);

	return err;

error:
	for (int i = 0; i < FUNC_MAX; i++)
	{
		Py_XDECREF(funcs[i]);
	}

	goto cleanup;
}

void
beer_script_free(struct BeerScript *script)
{
	if (script)
	{
		struct ScriptData *data = (struct ScriptData*)script->data_;
		for (int i = 0; i < FUNC_MAX; i++)
		{
			Py_XDECREF(data->funcs[i]);
		}
		free(script->data_);
		free(script);
	}
}

beer_err
beer_script_invoke_init(struct BeerScript *script)
{
	assert(script);
	return call(script, INIT_FUNC, "()");
}

beer_err
beer_script_invoke_fini(struct BeerScript *script)
{
	assert(script);
	return call(script, FINI_FUNC, "()");
}

beer_err
beer_script_invoke_update(struct BeerScript *script, float dt)
{
	assert(script);
	return call(script, UPDATE_FUNC, "(f)", dt);
}
