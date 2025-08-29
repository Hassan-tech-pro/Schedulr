# Schedulr
Schedulr is a smart timetable maker that removes conflicts between teachers, groups, and rooms. It takes a simple CSV file of courses and automatically creates a schedule using graph-based algorithms. No clashes, no wasted time — just a clean and fair timetable in seconds.



Problem Statement

Making timetables is hard. Teachers clash, groups overlap, and rooms double-book. Doing it by hand wastes hours and still leads to mistakes.



Solution Approach

Smart Scheduler is a graph-based scheduling tool built with Python + Streamlit.
Courses are nodes in a graph
Edges represent conflicts (same teacher or same group)
A greedy algorithm assigns time slots and rooms without conflicts
Output is a clean schedule in CSV format



Why it works

No manual slot assignment
Avoids teacher & group clashes
Supports multiple room types (lecture, lab, etc.)
Runs instantly after CSV upload



How to Run

Clone this repository
git clone https://github.com/yourusername/smart-scheduler.git
cd smart-scheduler


Install requirements

pip install -r requirements.txt

Run the app
streamlit run app.py


Upload your CSV file
Required columns:

course_id, course, group, teacher, duration, room_type

csv files provided.

Example Input (CSV)
course_id,course,group,teacher,duration,room_type
C1,Math,1,Smith,2,lecture
C2,Physics,1,Jones,2,lecture
C3,Chemistry,2,Smith,2,lab
C4,Biology,2,Brown,2,lab
C5,English,3,Davis,1,lecture

Example Output (CSV)
course_id	course	group	teacher	duration	assigned_slots	room
C1	Math	1	Smith	2	[Mon_9, Mon_10]	A
C2	Physics	1	Jones	2	[Mon_11, Mon_12]	B
C3	Chemistry	2	Smith	2	[Tue_9, Tue_10]	C
C4	Biology	2	Brown	2	[Tue_11, Tue_12]	D
C5	English	3	Davis	1	[Mon_13]	A
