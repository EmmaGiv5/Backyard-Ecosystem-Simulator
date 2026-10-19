extends Node2D
 
func _on_play_pressed():
	print("Play button was clicked") 
	get_tree().change_scene_to_file("res://saved.tscn")


func _on_credit_pressed():
	print("Credit button was clicked") 
	get_tree().change_scene_to_file("res://developers.tscn")


func _on_exit_pressed():
	print("Exit button was clicked") 
	get_tree().quit()
