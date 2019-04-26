def check_crash(player_x, player_y, bullet_x, bullet_y):
    if bullet_x - 73 < player_x < bullet_x + 73 and bullet_y -93 < player_y < bullet_y + 93:
        return True
    else:
        return False