# College Lab Slot Allocation using CSP
# AI Technique   : Constraint Satisfaction Problem
# Search Algorithm: Backtracking
#
# NOTE: The constraint logic and backtracking algorithm below are the exact
# same logic as the original console version. They have only been wrapped
# inside a class so the GUI (app.py) can call them with data
# collected from the screen instead of input().


class LabCSP:
    """
    Variables   : Each lab session (Session-1, Session-2, ...)
    Domain      : Every possible (Day, Lab, Slot) combination
    Constraints : 1. Lab capacity
                  2. Lab availability
                  3. Lab clash
                  4. Batch clash
                  5. Faculty availability
                  6. Faculty clash
    Search      : Backtracking Search
    """

    def __init__(self, labs, days, slots, sessions,
                 lab_availability, faculty_availability):
        self.labs = labs                             # {lab_name: capacity}
        self.days = days                             # [day1, day2, ...]
        self.slots = slots                           # [slot1, slot2, ...]
        self.sessions = sessions                      # {session: {...}}
        self.lab_availability = lab_availability       # {lab: {(day, slot)}}
        self.faculty_availability = faculty_availability  # {faculty: {(day, slot)}}

    # -----------------------------------------
    # CREATE DOMAINS
    # -----------------------------------------
    def create_domains(self):

        domains = {}

        for session in self.sessions:

            domains[session] = []

            for day in self.days:

                for lab in self.labs:

                    for slot in self.slots:

                        domains[session].append(
                            (day, lab, slot)
                        )

        return domains

    # -----------------------------------------
    # CHECK LAB AVAILABILITY
    # -----------------------------------------
    def lab_is_available(self, day, lab, slot):

        return (day, slot) in self.lab_availability[lab]

    # -----------------------------------------
    # CHECK FACULTY AVAILABILITY
    # -----------------------------------------
    def faculty_is_available(self, day, faculty, slot):

        return (day, slot) in self.faculty_availability[faculty]

    # -----------------------------------------
    # CHECK LAB CLASH
    # -----------------------------------------
    def lab_available(self, day, lab, slot, assignment):

        for session in assignment:

            assigned_day, assigned_lab, assigned_slot = assignment[session]

            if (assigned_day == day and
                assigned_lab == lab and
                assigned_slot == slot):

                return False

        return True

    # -----------------------------------------
    # CHECK BATCH CLASH
    # -----------------------------------------
    def batch_available(self, batch, day, slot, assignment):

        for session in assignment:

            assigned_day, assigned_lab, assigned_slot = assignment[session]

            if (self.sessions[session]["batch"] == batch and
                assigned_day == day and
                assigned_slot == slot):

                return False

        return True

    # -----------------------------------------
    # CHECK FACULTY CLASH
    # -----------------------------------------
    def faculty_available(self, faculty, day, slot, assignment):

        for session in assignment:

            assigned_day, assigned_lab, assigned_slot = assignment[session]

            if (self.sessions[session]["faculty"] == faculty and
                assigned_day == day and
                assigned_slot == slot):

                return False

        return True

    # -----------------------------------------
    # CHECK LAB CAPACITY
    # -----------------------------------------
    def capacity_available(self, session, lab):

        students = self.sessions[session]["students"]

        return students <= self.labs[lab]

    # -----------------------------------------
    # CHECK ALL CONSTRAINTS
    # -----------------------------------------
    def is_valid(self, session, day, lab, slot, assignment):

        batch = self.sessions[session]["batch"]
        faculty = self.sessions[session]["faculty"]

        # Constraint 1: Lab capacity
        if not self.capacity_available(session, lab):
            return False

        # Constraint 2: Lab availability
        if not self.lab_is_available(day, lab, slot):
            return False

        # Constraint 3: Lab clash
        if not self.lab_available(day, lab, slot, assignment):
            return False

        # Constraint 4: Batch clash
        if not self.batch_available(batch, day, slot, assignment):
            return False

        # Constraint 5: Faculty availability
        if not self.faculty_is_available(day, faculty, slot):
            return False

        # Constraint 6: Faculty clash
        if not self.faculty_available(faculty, day, slot, assignment):
            return False

        return True

    # -----------------------------------------
    # BACKTRACKING SEARCH
    # -----------------------------------------
    def solve(self, assignment, domains):

        # All sessions are assigned
        if len(assignment) == len(self.sessions):
            return assignment

        # Find an unassigned session
        session = None
        for s in self.sessions:
            if s not in assignment:
                session = s
                break

        # Try every possible Day + Lab + Slot
        for day, lab, slot in domains[session]:

            # Check all constraints
            if self.is_valid(session, day, lab, slot, assignment):

                # Make assignment
                assignment[session] = (day, lab, slot)

                # Solve remaining sessions
                result = self.solve(assignment, domains)

                if result is not None:
                    return result

                # Backtrack
                del assignment[session]

        # No valid assignment
        return None

    # -----------------------------------------
    # RUN THE FULL CSP (domains + backtracking)
    # -----------------------------------------
    def run(self):

        domains = self.create_domains()

        return self.solve({}, domains)
