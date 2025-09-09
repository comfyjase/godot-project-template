# Core

## Macros
These macros have been created to help reduce repeated code and provide automatic error checking.

### Editor Macros
Simplify binding properties for the editor.

Before:
```
void CustomSprite::_bind_methods() {
	ClassDB::bind_method(D_METHOD("get_amplitude"), &CustomSprite::get_amplitude);
	ClassDB::bind_method(D_METHOD("set_amplitude", "p_amplitude"), &CustomSprite::set_amplitude);
	ADD_PROPERTY(PropertyInfo(Variant::FLOAT, "amplitude"), "set_amplitude", "get_amplitude");
}
```

After:
```
void CustomSprite::_bind_methods() {
	GD_BIND_PROPERTY("amplitude", Variant::FLOAT, &CustomSprite::get_amplitude, &CustomSprite::set_amplitude);
}
```

### Pointer Macros
Simplify pointer assignments with error checks and optional error messages if the pointer is null.

Before:
```
Control *ui = get_node<Control>("CanvasLayer/UI");
ERR_FAIL_NULL(ui);
```

After:
```
GD_LOCAL_PTR(ui, get_node<Control>("CanvasLayer/UI"));
```

With a fail message.

Before:
```
Control *ui = get_node<Control>("CanvasLayer/UI");
ERR_FAIL_NULL_MSG(ui, "Failed to find CanvasLayer/UI node.");
```

After:
```
GD_LOCAL_PTR_MSG(ui, get_node<Control>("CanvasLayer/UI"), "Failed to find CanvasLayer/UI node.");
```

### Signal Macros
Checks signals aren't connected before trying to connect and provides any connect error messages if it fails.

Before:
```
if (!options_button->is_connected("pressed", callable_mp(this, &Game::show_options))) {
	const Error error = options_button->connect("pressed", callable_mp(this, &Game::show_options);
	ERR_FAIL_COND_MSG(error != Error::OK, String("Failed to connect to " + options_button->get_name().c_escape() + " pressed signal. Error: " + String::num_int64(error)));
}
```

After:
```
GD_CONNECT_SIGNAL(options_button, "pressed", &Game::show_options);
```
