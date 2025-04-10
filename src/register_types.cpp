#include "register_types.h"
#include <gdextension_interface.h>
#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/core/defs.hpp>
#include <godot_cpp/godot.hpp>

#if IMGUI_ENABLED
#include <imgui-godot.h>
#endif

#include "custom_sprite.h"

// Note, still want to include this class so the scene is always valid
// It's just, the class will basically be empty if IMGUI_ENABLED is not defined
// Which is as designed. This class should always exist.
#include "imgui_debug.h"

using namespace godot;

void initialize_gdextension_types(ModuleInitializationLevel p_level)
{
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE)
	{
		return;
	}

#if IMGUI_ENABLED
	ImGui::Godot::SyncImGuiPtrs();
#endif

	// Use GDREGISTER_CLASS if you want logic to run in editor as well...
	//GDREGISTER_CLASS(CustomSprite);
	GDREGISTER_RUNTIME_CLASS(ImGuiDebug);	// See comment above for #include "imgui_debug.h"
	GDREGISTER_RUNTIME_CLASS(CustomSprite);
}

void uninitialize_gdextension_types(ModuleInitializationLevel p_level)
{
	if (p_level != MODULE_INITIALIZATION_LEVEL_SCENE)
	{
		return;
	}
}

extern "C"
{
	// Initialization
	GDExtensionBool GDE_EXPORT game_library_init(GDExtensionInterfaceGetProcAddress p_get_proc_address, GDExtensionClassLibraryPtr p_library, GDExtensionInitialization *r_initialization)
	{
		GDExtensionBinding::InitObject init_obj(p_get_proc_address, p_library, r_initialization);
		init_obj.register_initializer(initialize_gdextension_types);
		init_obj.register_terminator(uninitialize_gdextension_types);
		init_obj.set_minimum_library_initialization_level(MODULE_INITIALIZATION_LEVEL_SCENE);

		return init_obj.init();
	}
}
