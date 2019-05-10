def check_crash(player_x, player_y, bullet_x, bullet_y):
    if bullet_x - 23 < player_x < bullet_x + 23 and bullet_y - 25 < player_y < bullet_y + 25:
        return True
    else:
        return False