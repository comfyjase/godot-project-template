#pragma once

#include <godot_cpp/classes/engine.hpp>
#include <godot_cpp/classes/global_constants.hpp>
#include <godot_cpp/classes/object.hpp>
#include <godot_cpp/core/binder_common.hpp>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/property_info.hpp>
#include <godot_cpp/core/type_info.hpp>
#include <godot_cpp/variant/string.hpp>
#include <godot_cpp/variant/typed_array.hpp>
#include <godot_cpp/variant/variant.hpp>

#define GD_BIND_METHOD(p_class, p_method_name, ...) /**********************************************************************************************************************************************************************************************************************/ \
    ClassDB::bind_method(D_METHOD(#p_method_name, ##__VA_ARGS__), &p_class::p_method_name);

#define GD_BIND_PROPERTY(p_class, p_name, p_type) /************************************************************************************************************************************************************************************************************************/ \
    {                                                                                                                                                                                                                                                                        \
        ClassDB::bind_method(D_METHOD("get_" #p_name), &p_class::get_##p_name);                                                                                                                                                                                              \
        ClassDB::bind_method(D_METHOD("set_" #p_name, "p_" #p_name), &p_class::set_##p_name);                                                                                                                                                                                \
        ADD_PROPERTY(PropertyInfo(p_type, #p_name), "set_" #p_name, "get_" #p_name);                                                                                                                                                                                         \
    }

#define GD_BIND_ENUM_PROPERTY(p_class, p_name, enum_values) /**************************************************************************************************************************************************************************************************************/ \
    {                                                                                                                                                                                                                                                                        \
        ClassDB::bind_method(D_METHOD("get_" #p_name), &p_class::get_##p_name);                                                                                                                                                                                              \
        ClassDB::bind_method(D_METHOD("set_" #p_name, "p_" #p_name), &p_class::set_##p_name);                                                                                                                                                                                \
        ADD_PROPERTY(godot::PropertyInfo(godot::Variant::INT, #p_name, godot::PROPERTY_HINT_ENUM, enum_values), "set_" #p_name, "get_" #p_name);                                                                                                                             \
    }

#define GD_BIND_REF_PROPERTY(p_class, p_name, p_type_hint) /***************************************************************************************************************************************************************************************************************/ \
    {                                                                                                                                                                                                                                                                        \
        ClassDB::bind_method(D_METHOD("get_" #p_name), &p_class::get_##p_name);                                                                                                                                                                                              \
        ClassDB::bind_method(D_METHOD("set_" #p_name, "p_" #p_name), &p_class::set_##p_name);                                                                                                                                                                                \
        ADD_PROPERTY(godot::PropertyInfo(godot::Variant::OBJECT, #p_name, godot::PROPERTY_HINT_RESOURCE_TYPE, p_type_hint), "set_" #p_name, "get_" #p_name);                                                                                                                 \
    }

#define GD_BIND_ARRAY_PROPERTY(p_class, p_name, p_hint_type) /*************************************************************************************************************************************************************************************************************/ \
    {                                                                                                                                                                                                                                                                        \
        ClassDB::bind_method(D_METHOD("get_" #p_name), &p_class::get_##p_name);                                                                                                                                                                                              \
        ClassDB::bind_method(D_METHOD("set_" #p_name, "p_" #p_name), &p_class::set_##p_name);                                                                                                                                                                                \
        ADD_PROPERTY(godot::PropertyInfo(godot::Variant::ARRAY, #p_name, godot::PropertyHint::PROPERTY_HINT_ARRAY_TYPE, p_hint_type), "set_" #p_name, "get_" #p_name);                                                                                                       \
    }

#define GD_BIND_RESOURCE_ARRAY_PROPERTY(p_class, p_name, p_hint_type) /****************************************************************************************************************************************************************************************************/ \
    {                                                                                                                                                                                                                                                                        \
        ClassDB::bind_method(D_METHOD("get_" #p_name), &p_class::get_##p_name);                                                                                                                                                                                              \
        ClassDB::bind_method(D_METHOD("set_" #p_name, "p_" #p_name), &p_class::set_##p_name);                                                                                                                                                                                \
        ADD_PROPERTY(godot::PropertyInfo(godot::Variant::ARRAY, #p_name, godot::PropertyHint::PROPERTY_HINT_TYPE_STRING, String::num(Variant::OBJECT) + "/" + String::num(PROPERTY_HINT_RESOURCE_TYPE) + p_hint_type), "set_" #p_name, "get_" #p_name);                      \
    }

#define GD_DISABLE_EDITOR_PROCESSING_FOR_NODE /****************************************************************************************************************************************************************************************************************************/ \
    if (Engine::get_singleton()->is_editor_hint()) {                                                                                                                                                                                                                         \
        static constexpr bool enabled = false;                                                                                                                                                                                                                               \
        set_process_input(enabled);                                                                                                                                                                                                                                          \
        set_process(enabled);                                                                                                                                                                                                                                                \
        set_physics_process(enabled);                                                                                                                                                                                                                                        \
        return;                                                                                                                                                                                                                                                              \
    }

#undef MAKE_TYPED_ARRAY_INFO
#undef MAKE_TYPED_ARRAY

#define MAKE_TYPED_ARRAY_INFO(m_type, m_variant_type) /********************************************************************************************************************************************************************************************************************/ \
    template <>                                                                                                                                                                                                                                                              \
    struct GetTypeInfo<TypedArray<m_type>> {                                                                                                                                                                                                                                 \
        static constexpr GDExtensionVariantType VARIANT_TYPE = GDEXTENSION_VARIANT_TYPE_ARRAY;                                                                                                                                                                               \
        static constexpr GDExtensionClassMethodArgumentMetadata METADATA = GDEXTENSION_METHOD_ARGUMENT_METADATA_NONE;                                                                                                                                                        \
        static inline PropertyInfo get_class_info() {                                                                                                                                                                                                                        \
            return make_property_info(Variant::Type::ARRAY, "", PROPERTY_HINT_ARRAY_TYPE, Variant::get_type_name(m_variant_type).utf8().get_data());                                                                                                                         \
        }                                                                                                                                                                                                                                                                    \
    };                                                                                                                                                                                                                                                                       \
    template <>                                                                                                                                                                                                                                                              \
    struct GetTypeInfo<const TypedArray<m_type> &> {                                                                                                                                                                                                                         \
        static constexpr GDExtensionVariantType VARIANT_TYPE = GDEXTENSION_VARIANT_TYPE_ARRAY;                                                                                                                                                                               \
        static constexpr GDExtensionClassMethodArgumentMetadata METADATA = GDEXTENSION_METHOD_ARGUMENT_METADATA_NONE;                                                                                                                                                        \
        static inline PropertyInfo get_class_info() {                                                                                                                                                                                                                        \
            return make_property_info(Variant::Type::ARRAY, "", PROPERTY_HINT_ARRAY_TYPE, Variant::get_type_name(m_variant_type).utf8().get_data());                                                                                                                         \
        }                                                                                                                                                                                                                                                                    \
    };

#define MAKE_TYPED_ARRAY(m_type, m_variant_type) /*************************************************************************************************************************************************************************************************************************/ \
    template <>                                                                                                                                                                                                                                                              \
    class TypedArray<m_type> : public Array {                                                                                                                                                                                                                                \
    public:                                                                                                                                                                                                                                                                  \
        _FORCE_INLINE_ void operator=(const Array &p_array) {                                                                                                                                                                                                                \
            ERR_FAIL_COND_MSG(!is_same_typed(p_array), "Cannot assign an array with a different element type.");                                                                                                                                                             \
            Array::operator=(p_array);                                                                                                                                                                                                                                       \
        }                                                                                                                                                                                                                                                                    \
        _FORCE_INLINE_ TypedArray(std::initializer_list<Variant> p_init) :                                                                                                                                                                                                   \
                Array(Array(p_init), m_variant_type, StringName(), Variant()) {                                                                                                                                                                                              \
        }                                                                                                                                                                                                                                                                    \
        _FORCE_INLINE_ TypedArray(const Variant &p_variant) :                                                                                                                                                                                                                \
                TypedArray(Array(p_variant)) {                                                                                                                                                                                                                               \
        }                                                                                                                                                                                                                                                                    \
        _FORCE_INLINE_ TypedArray(const Array &p_array) {                                                                                                                                                                                                                    \
            set_typed(m_variant_type, StringName(), Variant());                                                                                                                                                                                                              \
            if (is_same_typed(p_array)) {                                                                                                                                                                                                                                    \
                Array::operator=(p_array);                                                                                                                                                                                                                                   \
            } else {                                                                                                                                                                                                                                                         \
                assign(p_array);                                                                                                                                                                                                                                             \
            }                                                                                                                                                                                                                                                                \
        }                                                                                                                                                                                                                                                                    \
        _FORCE_INLINE_ TypedArray() {                                                                                                                                                                                                                                        \
            set_typed(m_variant_type, StringName(), Variant());                                                                                                                                                                                                              \
        }                                                                                                                                                                                                                                                                    \
    };
