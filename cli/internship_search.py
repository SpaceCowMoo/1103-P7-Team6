from cli.screen import Screen

# Search internship option
# Searching mainly uses SQL queries/ functions from DBmanager
class InternshipSearch(Screen):
    SEARCH = -1
    CANCEL = -2

    # db filter names are different to what user will see
    FILTER_FIELDS = {
        0: ("Job ID", "job_id"),
        1: ("Company name", "company_name"),
        2: ("Company type", "company_type"),
        3: ("Industry", "industry"),
        4: ("Job title", "job_title"),
        5: ("Relevant course", "relevant_course"),
        6: ("Monthly allowance", "monthly_allowance"),
        7: ("Work mode", "work_mode"),
        8: ("Duration (months)", "duration_months"),
        9: ("Required skills", "required_skills"),
        10: ("Location", "location_district"),
    }

    def __init__(self, context):
        super().__init__(context)
        self.__filters = {}

    def run(self):
        last = len(self.FILTER_FIELDS) - 1
        while True:
            self.show_fields()
            self.show_active_filters()
            choice = self._input.ask_int(
                f"Pick a field (0-{last}), -1 to search, -2 to cancel:", self.CANCEL, last)
            if choice == self.CANCEL:
                return                  
            if choice == self.SEARCH:
                break                   
            self.add_filter(choice)

        results = self._data.list_internships(limit= -1, partial=True, **self.__filters)
        self._display.message(f"Found {len(results)} internship(s).")
        self._page_through(results, self._display.internship)   

    def add_filter(self, number):
        label, column = self.FILTER_FIELDS[number]
        text = self._input.ask(f"Search {label} for:").strip()
        self.__filters[column] = text     

    def show_fields(self):
        display = self._display
        display.heading("FILTER OPTIONS")
        for number, (label, column) in self.FILTER_FIELDS.items():
            display.message(f"  {number:>2} : {label}")
        display.line()

    def show_active_filters(self):
        if not self.__filters:
            return                      
        parts = []
        for number, (label, column) in self.FILTER_FIELDS.items():
            if column in self.__filters:
                parts.append(f"{label} = {self.__filters[column]}")
        self._display.message("Current filters: " + ", ".join(parts))