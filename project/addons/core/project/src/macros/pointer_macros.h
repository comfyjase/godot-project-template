#pragma once

#include <godot_cpp/classes/ref.hpp>
#include <godot_cpp/core/error_macros.hpp>

#define GD_PTR(variable, value) /******************************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_NULL(variable);

#define GD_PTR_RET(variable, value, return_value) /************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_NULL_V(variable, return_value);

#define GD_PTR_MSG(variable, value, fail_message) /************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_NULL_MSG(variable, fail_message);

#define GD_PTR_MSG_RET(variable, value, fail_message, return_value) /******************************/ \
    variable = value;                                                                                \
    ERR_FAIL_NULL_V_MSG(variable, return_value, fail_message);

#define GD_LOCAL_PTR(variable, value) /************************************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_NULL(variable);

#define GD_LOCAL_PTR_RET(variable, value, return_value) /******************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_NULL_V(variable, return_value);

#define GD_LOCAL_PTR_MSG(variable, value, fail_message) /******************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_NULL_MSG(variable, fail_message);

#define GD_LOCAL_PTR_MSG_RET(variable, value, fail_message, return_value) /************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_NULL_V_MSG(variable, return_value, fail_message);

#define GD_REF(variable, value) /******************************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_COND(!variable.is_valid());

#define GD_REF_RET(variable, value, return_value) /************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_COND_V(!variable.is_valid(), return_value);

#define GD_REF_MSG(variable, value, fail_message) /************************************************/ \
    variable = value;                                                                                \
    ERR_FAIL_COND_MSG(!variable.is_valid(), fail_message);

#define GD_REF_MSG_RET(variable, value, fail_message, return_value) /******************************/ \
    variable = value;                                                                                \
    ERR_FAIL_COND_V_MSG(!variable.is_valid(), return_value, fail_message);

#define GD_LOCAL_REF(variable, value) /************************************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_COND(!variable.is_valid());

#define GD_LOCAL_REF_RET(variable, value, return_value) /******************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_COND_V(!variable.is_valid(), return_value);

#define GD_LOCAL_REF_MSG(variable, value, fail_message) /******************************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_COND_MSG(!variable.is_valid(), fail_message);

#define GD_LOCAL_REF_MSG_RET(variable, value, fail_message, return_value) /************************/ \
    auto variable = value;                                                                           \
    ERR_FAIL_COND_V_MSG(!variable.is_valid(), return_value, fail_message);

#define GD_LOCAL_REF_VARIANT(ref_type, variable, value) /******************************************/ \
    const godot::Ref<ref_type> variable = value;                                                     \
    ERR_FAIL_COND(!variable.is_valid());

#define GD_LOCAL_REF_VARIANT_RET(ref_type, variable, value, return_value) /************************/ \
    const godot::Ref<ref_type> variable = value;                                                     \
    ERR_FAIL_COND_V(!variable.is_valid(), return_value);

#define GD_LOCAL_REF_VARIANT_MSG(ref_type, variable, value, fail_message) /************************/ \
    const godot::Ref<ref_type> variable = value;                                                     \
    ERR_FAIL_COND_MSG(!variable.is_valid(), fail_message);

#define GD_LOCAL_REF_VARIANT_MSG_RET(ref_type, variable, value, fail_message, return_value) /******/ \
    const godot::Ref<ref_type> variable = value;                                                     \
    ERR_FAIL_COND_MSG(!variable.is_valid(), fail_message);
