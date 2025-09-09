#pragma once

#include <godot_cpp/classes/node.hpp>

namespace godot {

class GameTest : public Node {
	GDCLASS(GameTest, Node)

protected:
	static void _bind_methods();

public:
	GameTest();
	~GameTest();

	void _ready() override;
};

} //namespace godot
