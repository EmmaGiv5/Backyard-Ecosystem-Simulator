extends Node2D

func on_game1_pressed():
	print("Game 1 selected")
	get_tree().change_scene_to_file("res://Scenes/user.tscn")
	
func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		print("Escape key pressed")
		get_tree().change_scene_to_file("res://Scenes/main_menu.tscn")
