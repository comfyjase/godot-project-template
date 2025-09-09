#pragma once

#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/node.hpp>
#include <godot_cpp/core/error_macros.hpp>
#include <godot_cpp/variant/callable_method_pointer.hpp>
#include <godot_cpp/variant/string.hpp>

#define GD_CONNECT_SIGNAL_OBJECT(object, signal_name, signal_function) /******************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (!object->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                       \
			const godot::Error error = object->connect(signal_name, callable_mp(this, signal_function));                                                                                                                                    \
			ERR_FAIL_COND_MSG(error != godot::Error::OK, godot::String("Failed to connect to " + object->to_string().c_escape() + " " + godot::String(signal_name) + " signal. Error: " + godot::String::num_int64(error)));                \
		}                                                                                                                                                                                                                                   \
	}

#define GD_CONNECT_SIGNAL(node, signal_name, signal_function) /***************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (!node->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                         \
			const godot::Error error = node->connect(signal_name, callable_mp(this, signal_function));                                                                                                                                      \
			ERR_FAIL_COND_MSG(error != godot::Error::OK, godot::String("Failed to connect to " + node->get_name().c_escape() + " " + godot::String(signal_name) + " signal. Error: " + godot::String::num_int64(error)));                   \
		}                                                                                                                                                                                                                                   \
	}

#define GD_CONNECT_SIGNAL_RET(node, signal_name, signal_function, return_value) /*********************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (!node->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                         \
			const godot::Error error = node->connect(signal_name, callable_mp(this, signal_function));                                                                                                                                      \
			ERR_FAIL_COND_V_MSG(error != godot::Error::OK, return_value, godot::String("Failed to connect to " + node->get_name().c_escape() + " " + godot::String(signal_name) + " signal. Error: " + godot::String::num_int64(error)));   \
		}                                                                                                                                                                                                                                   \
	}

#define GD_CONNECT_SIGNAL_MSG(node, signal_name, signal_function, fail_message) /*********************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (!node->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                         \
			const godot::Error error = node->connect(signal_name, callable_mp(this, signal_function));                                                                                                                                      \
			ERR_FAIL_COND_MSG(error != godot::Error::OK, fail_message + godot::String(" Error: " + godot::String::num_int64(error)));                                                                                                       \
		}                                                                                                                                                                                                                                   \
	}

#define GD_CONNECT_SIGNAL_MSG_RET(node, signal_name, signal_function, fail_message, return_value) /***************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (!node->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                         \
			const godot::Error error = node->connect(signal_name, callable_mp(this, signal_function));                                                                                                                                      \
			ERR_FAIL_COND_V_MSG(error != godot::Error::OK, return_value, fail_message + godot::String(" Error: " + godot::String::num_int64(error)));                                                                                       \
		}                                                                                                                                                                                                                                   \
	}

#define GD_EMIT_SIGNAL_OBJECT(object, signal_name, ...) /*********************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		const godot::Error error = object->emit_signal(signal_name, ##__VA_ARGS__);                                                                                                                                                         \
		ERR_FAIL_COND_MSG(error != godot::Error::OK, godot::String("Failed to emit signal " + godot::String(signal_name) + " from " + object->to_string().c_escape() + ". Error: " + godot::String::num_int64(error)));                     \
	}

#define GD_EMIT_SIGNAL(node, signal_name, ...) /******************************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		const godot::Error error = node->emit_signal(signal_name, ##__VA_ARGS__);                                                                                                                                                           \
		ERR_FAIL_COND_MSG(error != godot::Error::OK, godot::String("Failed to emit signal " + godot::String(signal_name) + " from " + node->get_name().c_escape() + ". Error: " + godot::String::num_int64(error)));                        \
	}

#define GD_EMIT_SIGNAL_RET(node, signal_name, return_value, ...) /************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		const godot::Error error = node->emit_signal(signal_name, ##__VA_ARGS__);                                                                                                                                                           \
		ERR_FAIL_COND_V_MSG(error != godot::Error::OK, return_value, godot::String("Failed to emit signal " + godot::String(signal_name) + " from " + node->get_name().c_escape() + ". Error: " + godot::String::num_int64(error)));        \
	}

#define GD_EMIT_SIGNAL_MSG(node, signal_name, fail_message, ...) /************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		const godot::Error error = node->emit_signal(signal_name, ##__VA_ARGS__);                                                                                                                                                           \
		ERR_FAIL_COND_MSG(error != godot::Error::OK, fail_message + godot::String(" Error: " + godot::String::num_int64(error)));                                                                                                           \
	}

#define GD_EMIT_SIGNAL_MSG_RET(node, signal_name, fail_message, return_value, ...) /******************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		const godot::Error error = node->emit_signal(signal_name, ##__VA_ARGS__);                                                                                                                                                           \
		ERR_FAIL_COND_V_MSG(error != godot::Error::OK, return_value, fail_message + godot::String(" Error: " + godot::String::num_int64(error)));                                                                                           \
	}

#define GD_DISCONNECT_SIGNAL(node, signal_name, signal_function) /************************************************************************************************************************************************************************/ \
	{                                                                                                                                                                                                                                       \
		if (node->is_connected(signal_name, callable_mp(this, signal_function))) {                                                                                                                                                          \
			node->disconnect(signal_name, callable_mp(this, signal_function));                                                                                                                                                              \
		}                                                                                                                                                                                                                                   \
	}
