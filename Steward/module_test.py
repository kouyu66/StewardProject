#!/usr/bin/env python3
# Coding:UTF-8

card_remove  = []
card_add = []        
current_card_info = ['ssd1', 'ssd2']
last_card_info = ['ssd3']

for current_card in current_card_info:
    if current_card not in last_card_info:
        card_add.append(current_card)
    else:
        last_card_info.remove(current_card)
if last_card_info:
    card_remove = last_card_info

print(card_add)
print(card_remove)