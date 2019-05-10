def check_crash(player_x, player_y, bullet_x, bullet_y):
    if bullet_x - 32 < player_x < bullet_x + 32 and bullet_y - 33 < player_y < bullet_y + 33:
        return True
    else:
        return False