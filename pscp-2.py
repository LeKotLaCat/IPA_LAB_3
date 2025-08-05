import random
import sys
import os

# --- การตั้งค่าพื้นฐาน (ปรับแต่งได้) ---
CONFIG = {
    "value_range": (1, 1000),      # มูลค่าสมบัติ
    "zero_probability": 0.15,      # โอกาสเจอหีบเปล่า
    "output_folder": "testcases"   # ชื่อโฟลเดอร์ที่จะเก็บไฟล์
}

def solve_case(n, k, y, treasures):
    """
    ฟังก์ชันสำหรับแก้โจทย์ตาม Input ที่ได้รับ เพื่อหาคำตอบที่ถูกต้อง
    """
    chests_opened = 0
    current_treasure = 0
    
    for i in range(k - 1, n):
        chests_opened += 1
        value = treasures[i]
        
        if value == 0:
            current_treasure = 0
        else:
            current_treasure += value
            
        if current_treasure >= y:
            break
            
    if current_treasure >= y:
        return f"{chests_opened}\n{current_treasure}"
    else:
        return f"Give up\n{current_treasure}"

def generate_treasures(n, has_zero):
    """สร้างรายการสมบัติ"""
    treasures = [random.randint(CONFIG['value_range'][0], CONFIG['value_range'][1]) for _ in range(n)]
    if has_zero and n > 1:
        num_zeros = random.randint(1, max(1, int(n * CONFIG['zero_probability'])))
        for _ in range(num_zeros):
            while True:
                pos = random.randint(0, n - 1)
                if treasures[pos] != 0:
                    treasures[pos] = 0
                    break
    return treasures

def simulate_run_for_y(treasures, k):
    """จำลองการเล่นเกมเพื่อหาผลรวมสุดท้าย (สำหรับใช้สร้างค่า y)"""
    n = len(treasures)
    current_treasure = 0
    for i in range(k - 1, n):
        value = treasures[i]
        if value == 0:
            current_treasure = 0
        else:
            current_treasure += value
    return current_treasure

def generate_case(case_type, n, base_filename=""):
    """
    ฟังก์ชันหลักในการสร้างชุดทดสอบและคำตอบ และเซฟลงไฟล์
    """
    if n <= 0:
        print("Error: Number of chests (n) must be positive.", file=sys.stderr)
        return

    # สร้างข้อมูล Input
    if "start_1" in case_type: k = 1
    elif "edge_k_gt_n" in case_type: k = n + random.randint(1, 5)
    elif "edge_k_eq_n" in case_type: k = n
    else: k = random.randint(2, n) if n > 1 else 1
    has_zero = "with_reset" in case_type
    treasures = generate_treasures(n, has_zero)
    final_sum = simulate_run_for_y(treasures, k)
    
    y = 0
    if "fail" in case_type:
        y = final_sum + random.randint(1, 500)
    elif "exact" in case_type:
        if final_sum == 0: return generate_case(case_type, n, base_filename)
        y = final_sum
    else: # "early_success"
        if final_sum <= 1: return generate_case(case_type, n, base_filename)
        y = random.randint(1, final_sum - 1)

    # เตรียมข้อมูลสำหรับเขียนลงไฟล์
    input_data = f"{n}\n{k}\n{y}\n" + "\n".join(map(str, treasures))
    expected_output = solve_case(n, k, y, treasures)

    # --- ส่วนของการเขียนไฟล์ ---
    if not os.path.exists(CONFIG['output_folder']):
        os.makedirs(CONFIG['output_folder'])

    # กำหนดชื่อไฟล์
    if not base_filename:
        i = 1
        while True:
            filename = f"test_case_{i}"
            if not os.path.exists(os.path.join(CONFIG['output_folder'], f"{filename}.in")):
                base_filename = filename
                break
            i += 1
            
    input_filepath = os.path.join(CONFIG['output_folder'], f"{base_filename}.in")
    output_filepath = os.path.join(CONFIG['output_folder'], f"{base_filename}.ans")

    try:
        # เขียนไฟล์ Input
        with open(input_filepath, "w", encoding="utf-8") as f_in:
            f_in.write(input_data)
        
        # เขียนไฟล์ Output (Answer)
        with open(output_filepath, "w", encoding="utf-8") as f_out:
            f_out.write(expected_output)
            
        print(f"\nSuccessfully created files:")
        print(f"  Input:   {input_filepath}")
        print(f"  Answer:  {output_filepath}")

    except IOError as e:
        print(f"\nError writing to file: {e}", file=sys.stderr)


# --- เมนูหลัก ---
def main_menu():
    case_map = {
        1: ("no_reset_fail_start_1", "ไม่คืนเงิน, ไม่สำเร็จ, เริ่มที่ 1"),
        # ... (เหมือนเดิม)
        15: ("edge_k_eq_n_early_success", "Edge Case: k = n, สำเร็จ"),
    }
    # (โค้ดส่วนแสดงผลเมนูเหมือนเดิม)
    # ...
    
    while True:
        # (โค้ดส่วนแสดงเมนูและรับ choice เหมือนเดิม)
        # ...

        # คำถามเพิ่มเติม: ชื่อไฟล์
        filename_input = input("Enter a base filename (e.g., case01) or press Enter for auto-naming: ").strip()

        print("\nGenerating and saving files...")
        case_type, _ = case_map[choice_num]
        generate_case(case_type, n, filename_input)

        input("\nPress Enter to return to the menu...")

# เพื่อให้โค้ดสั้นลง จะย่อส่วนเมนูที่เหมือนเดิม
def main_menu():
    case_map = {
        1: ("no_reset_fail_start_1", "ไม่คืนเงิน, ไม่สำเร็จ, เริ่มที่ 1"), 2: ("no_reset_exact_start_1", "ไม่คืนเงิน, สำเร็จพอดี, เริ่มที่ 1"), 3: ("no_reset_early_success_start_1", "ไม่คืนเงิน, สำเร็จก่อน, เริ่มที่ 1"), 4: ("no_reset_fail_start_k", "ไม่คืนเงิน, ไม่สำเร็จ, เริ่มที่ K"), 5: ("no_reset_exact_start_k", "ไม่คืนเงิน, สำเร็จพอดี, เริ่มที่ K"), 6: ("no_reset_early_success_start_k", "ไม่คืนเงิน, สำเร็จก่อน, เริ่มที่ K"), 7: ("with_reset_fail_start_1", "ต้องคืนเงิน, ไม่สำเร็จ, เริ่มที่ 1"), 8: ("with_reset_exact_start_1", "ต้องคืนเงิน, สำเร็จพอดี, เริ่มที่ 1"), 9: ("with_reset_early_success_start_1", "ต้องคืนเงิน, สำเร็จก่อน, เริ่มที่ 1"), 10: ("with_reset_fail_start_k", "ต้องคืนเงิน, ไม่สำเร็จ, เริ่มที่ K"), 11: ("with_reset_exact_start_k", "ต้องคืนเงิน, สำเร็จพอดี, เริ่มที่ K"), 12: ("with_reset_early_success_start_k", "ต้องคืนเงิน, สำเร็จก่อน, เริ่มที่ K"), 13: ("edge_k_gt_n_fail", "Edge Case: k > n"), 14: ("edge_k_eq_n_fail", "Edge Case: k = n, ไม่สำเร็จ"), 15: ("edge_k_eq_n_early_success", "Edge Case: k = n, สำเร็จ"),
    }

    while True:
        print("\n" + "="*50)
        print("Please choose a test case to generate:")
        for num, (_, desc) in case_map.items():
            print(f"  {num:2d}. {desc}")
        print("\nEnter 'q' to quit.")
        print("="*50)
        
        choice = input("Enter your choice: ")
        if choice.lower() == 'q': print("Exiting."); break
        
        try:
            choice_num = int(choice)
            if choice_num not in case_map: raise ValueError
        except ValueError:
            print("\n*** Invalid choice. ***"); continue

        n_input = input("Enter the number of chests (n) for this case: ")
        try:
            n = int(n_input)
        except ValueError:
            print("\n*** Invalid number for n. ***"); continue
        
        filename_input = input("Enter a base filename (e.g., case01) or press Enter for auto-naming: ").strip()

        print("\nGenerating and saving files...")
        case_type, _ = case_map[choice_num]
        generate_case(case_type, n, filename_input)

        input("\nPress Enter to return to the menu...")


if __name__ == "__main__":
    main_menu()