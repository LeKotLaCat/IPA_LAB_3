n = int(input())
k = int(input())
y = int(input())

chests_counted = 0
current_treasure = 0
goal_reached = False

for i in range(1, n + 1):
    value = int(input())
    if i >= k and not goal_reached:
        chests_counted += 1
        
        if value == 0:
            current_treasure = 0
        else:
            current_treasure += value
        if current_treasure >= y:
            goal_reached = True

if current_treasure >= y:
    print(chests_counted)
    print(current_treasure)
else:
    print("Give up")
    print(current_treasure)



# Case 1 เริ่มจากกล่องแรก ไม่ต้องคืนเงินกลับไป ได้เงินไม่ครบ (กล่องหมดก่อน) 
# Case 2 เริ่มจากกล่องแรก ไม่ต้องคืนเงินกลับไป ได้เงินครบ (กล่องพอดี)
# Case 3 เริ่มจากกล่องแรก ไม่ต้องคืนเงินกลับไป ได้เงินครบ (กล่องเหลือ)

# Case 4 เริ่มจากกล่องที่ K ไม่ต้องคืนเงินกลับไป ได้เงินไม่ครบ (กล่องหมดก่อน) 
# Case 5 เริ่มจากกล่องที่ K ไม่ต้องคืนเงินกลับไป ได้เงินครบ (กล่องพอดี)
# Case 6 เริ่มจากกล่องที่ K ไม่ต้องคืนเงินกลับไป ได้เงินครบ (กล่องเหลือ)

# Case 7 เริ่มจากกล่องแรก ต้องคืนเงินกลับไป ได้เงินไม่ครบ (กล่องหมดก่อน) 
# Case 8 เริ่มจากกล่องแรก ต้องคืนเงินกลับไป ได้เงินครบ (กล่องพอดี)
# Case 9 เริ่มจากกล่องแรก ต้องคืนเงินกลับไป ได้เงินครบ (กล่องเหลือ)

# Case 10 เริ่มจากกล่องที่ K ต้องคืนเงินกลับไป ได้เงินไม่ครบ (กล่องหมดก่อน) 
# Case 11 เริ่มจากกล่องที่ K ต้องคืนเงินกลับไป ได้เงินครบ (กล่องพอดี)
# Case 12 เริ่มจากกล่องที่ K ต้องคืนเงินกลับไป ได้เงินครบ (กล่องเหลือ)

#Edge Case
# Case 13 เริ่มจากกล่องที่ K แต่ K > N
# Case 14 เริ่มจากกล่องที่ K แต่ K == N





