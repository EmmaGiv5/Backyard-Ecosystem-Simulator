extends Node2D

func _on_start_game1_pressed():
	print("Start pressed")
	get_tree().change_scene_to_file("res://Scenes/backyard.tscn")

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		print("Escape key pressed")
		get_tree().change_scene_to_file("res://Scenes/saved.tscn")
