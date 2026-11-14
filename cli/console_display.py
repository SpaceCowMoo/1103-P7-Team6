#The only class that calls print(). Every heading, message, error and card goes through it, so changing how the app looks means editing one file.
WIDTH = 60

class ConsoleDisplay:
    
    def __init__(self):
        self.__width = WIDTH

    def line(self):
        print("="* self.__width)

    def divider(self):
        print("-" * self.__width)

    def heading(self, title):
        self.line()
        print(f"{title:^{self.__width}}")
        self.line()

    def message(self, *values):
        print(*values)

    def error(self, text):
        print(f"  ERROR : {text}")

    def numbered_list(self, items):
        for value, content in enumerate(items, start=1):
            print(f"{value} : {content}")
            
    def card(self, title, fields):
        self.heading(title)
        for label, value in fields:
            if value is None or value == "":
                value = "Not specified"
            print(f"{label}: {value}")

    def get_width(self):
        return self.__width

    # Set up using Internship class
    # Put it here for printing
    def internship(self, internship):
        allowance = internship.get_monthly_allowance()
        self.card("INTERNSHIP LISTING", [
        ("Job ID", internship.get_job_id()),
        ("Company", internship.get_company_name()),
        ("Role", internship.get_job_title()),
        ("Industry", internship.get_industry()),
        ("Work mode", internship.get_work_mode()),
        ("Location", internship.get_location_district()),
        ("Allowance", f"${allowance}" if allowance is not None else None),
        ("Duration", f"{internship.get_duration_months()} months"),
        ("Skills", internship.get_required_skills()),
        ("Description", internship.get_job_description()),
    ])

    def run_summary(self, run):
        """The top match of the AI's feedback."""
        best = run.get_results()[0]                      
        self.card(f"RUN #{run.get_run_id()}", [
            ("Date", run.get_created_at()),
            ("Top match", best.get_listing().get_internship().get_job_title()),
            ("Top score", f"{best.get_score():.1f}"),
            ("Feedback", "\n".join(run.get_feedback())),   
        ])

    def run_result(self, result):
        """One of the 5 matches inside a run."""
        listing = result.get_listing()
        internship = listing.get_internship()
        flags = [flag.get_flag_name() for flag in listing.get_Flags()]
        self.card(f"MATCH {result.get_rank()}", [
            ("Role", internship.get_job_title()),
            ("Company", internship.get_company_name()),
            ("Score", f"{result.get_score():.1f}"),
            ("Flags", ", ".join(flags) if flags else "None"),
        ])