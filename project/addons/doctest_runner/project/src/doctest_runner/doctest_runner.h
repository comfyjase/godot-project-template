#pragma once

#include <godot_cpp/classes/node.hpp>

namespace godot {

class DoctestRunner : public Node {
	GDCLASS(DoctestRunner, Node);

protected:
	static void _bind_methods();

public:
	DoctestRunner();
	~DoctestRunner();

	void _ready() override;

private:
	int number_of_finished_test_runs;
	int return_code;

	void test_runner_finished(Node *p_node, int p_return_code);
	void all_test_runners_finished();
};

} //namespace godot
