import csv
import json
from pathlib import Path

JSON_FILE = Path("students.json")
CSV_FILE = Path("students.csv")


def load_records(filepath: Path = JSON_FILE) -> list[dict]:
  """Load student records from a JSON file safely."""
  if not filepath.exists():
    return []
  try:
    with filepath.open("r", encoding="utf-8") as file:
      data = json.load(file)
      return data if isinstance(data, list) else []
  except (json.JSONDecodeError, OSError) as exc:
    print(f"Warning: Could not read {filepath} ({exc}). Starting fresh.")
    return []


def save_records(records: list[dict], filepath: Path = JSON_FILE) -> None:
  """Persist student records to JSON."""
  with filepath.open("w", encoding="utf-8") as file:
    json.dump(records, file, indent=2)


def export_to_csv(records: list[dict], filepath: Path = CSV_FILE) -> None:
  """Export student records to a CSV file."""
  fieldnames = ["id", "name", "course", "marks", "average"]
  with filepath.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for r in records:
      row = r.copy()
      row["marks"] = ";".join(str(m) for m in r["marks"])
      writer.writerow(row)


def calculate_average(*marks: float) -> float:
  """Calculate average from variable number of mark arguments (*args)."""
  return round(sum(marks) / len(marks), 2) if marks else 0.0


def add_student(
    records: list[dict],
    student_id: str,
    name: str,
    course: str,
    marks: list[float],
) -> None:
  """Create a new student record if ID is unique."""
  if not student_id or not name.strip():
    raise ValueError("Student ID and Name cannot be empty.")
  if any(s["id"] == student_id for s in records):
    raise ValueError(f"Student with ID '{student_id}' already exists.")
  if any(m < 0 or m > 100 for m in marks):
    raise ValueError("Marks must be between 0 and 100.")

  records.append({
      "id": student_id,
      "name": name.strip(),
      "course": course.strip() or "General",
      "marks": marks,
      "average": calculate_average(*marks),
  })


def search_students(records: list[dict], query: str) -> list[dict]:
  """Search students by exact ID or partial case-insensitive name."""
  q = query.strip().lower()
  return [s for s in records if s["id"].lower() == q or q in s["name"].lower()]


def update_student(
    records: list[dict], student_id: str, **updates
) -> bool:
  """Update arbitrary student fields using **kwargs."""
  matches = [s for s in records if s["id"] == student_id]
  if not matches:
    return False
  student = matches[0]

  for key, value in updates.items():
    if value is not None and value != "":
      student[key] = value
      if key == "marks":
        student["average"] = calculate_average(*value)
  return True


def delete_student(records: list[dict], student_id: str) -> bool:
  """Delete a student record by ID."""
  initial_len = len(records)
  records[:] = [s for s in records if s["id"] != student_id]
  return len(records) < initial_len


def main() -> None:
  records = load_records()

  while True:
    print("\n--- Student Record Management System ---")
    print("1. Add Student")
    print("2. View All Students (Ranked by Average)")
    print("3. Search Student (by ID or Name)")
    print("4. Update Student Details / Marks")
    print("5. Delete Student")
    print("6. Export Records to CSV")
    print("7. Exit")

    choice = input("Enter choice (1-7): ").strip()

    try:
      if choice == "1":
        sid = input("Student ID: ").strip()
        name = input("Name: ").strip()
        course = input("Course: ").strip()
        raw_marks = input("Enter 3 marks separated by commas: ").strip()
        marks = [float(x.strip()) for x in raw_marks.split(",") if x.strip()]
        if len(marks) != 3:
          raise ValueError("Please enter exactly 3 numeric marks.")
        add_student(records, sid, name, course, marks)
        save_records(records)
        print("Student added successfully.")

      elif choice == "2":
        if not records:
          print("No student records found.")
        else:
          ranked = sorted(records, key=lambda s: s["average"], reverse=True)
          for s in ranked:
            print(
                f"ID: {s['id']} | Name: {s['name']} | Course: {s.get('course', 'N/A')} | "
                f"Marks: {s['marks']} | Avg: {s['average']}"
            )

      elif choice == "3":
        query = input("Enter Student ID or Name to search: ").strip()
        results = search_students(records, query)
        if results:
          for s in results:
            print(s)
        else:
          print("No matching student found.")

      elif choice == "4":
        sid = input("Enter Student ID to update: ").strip()
        new_name = input("New Name (leave blank to keep current): ").strip()
        new_course = input("New Course (leave blank to keep current): ").strip()
        raw_marks = input("New Marks comma-separated (leave blank to keep): ").strip()

        updates = {}
        if new_name:
          updates["name"] = new_name
        if new_course:
          updates["course"] = new_course
        if raw_marks:
          marks = [float(x.strip()) for x in raw_marks.split(",") if x.strip()]
          if any(m < 0 or m > 100 for m in marks):
            raise ValueError("Marks must be between 0 and 100.")
          updates["marks"] = marks

        if update_student(records, sid, **updates):
          save_records(records)
          print("Student record updated.")
        else:
          print("Student ID not found.")

      elif choice == "5":
        sid = input("Enter Student ID to delete: ").strip()
        if delete_student(records, sid):
          save_records(records)
          print("Record deleted.")
        else:
          print("Student ID not found.")

      elif choice == "6":
        export_to_csv(records)
        print(f"Exported {len(records)} records to {CSV_FILE}.")

      elif choice == "7":
        save_records(records)
        print("Exiting. All changes saved.")
        break

      else:
        print("Invalid choice. Select between 1 and 7.")

    except ValueError as err:
      print(f"Validation / Input Error: {err}")
    except Exception as err:
      print(f"Unexpected Error: {err}")
    finally:
      pass  # Hook for audit logging or resource cleanup


if __name__ == "__main__":
  main()
