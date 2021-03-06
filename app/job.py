from re import sub
from decimal import Decimal


class Job:

    def __parse_extras(self, line: str) -> None:
        """
        Parse extra fields from a full Job info
        :param line: single line from job info chunk
        :return:
        """
        job_types = ["Full-time", "Freelance", "Apprenticeship", "Volunteer", "Casual", "Commission", "Fly-In/Fly-Out",
                     "Contract", "Part-time", "Permanent", "Internship", "Temporary", "Temporarily remote", "Remote"]
        salary_info = line.split('-')
        currency = [s for s in salary_info if "$" in s]
        if currency:
            self.salary_base = Decimal(sub(r'[^\d.]', '', currency[0]))
            if len(currency) > 1:
                self.salary_upper = Decimal(sub(r'[^\d.]', '', currency[1]))
        job_types = [s for s in salary_info if "$" not in s and s in job_types]
        self.job_type = None if "-".join(job_types) == '' else "-".join(job_types)

    def __init__(self, title: str, company: str, location: str, job_description: str, extra_info: str):
        """
        Initialization of Job objects
        :param title:
        :param company:
        :param location:
        :param job_description:
        :param extra_info:
        """
        # initialization handles sanitization of data
        self.title = title
        self.company = company
        self.location = location.lstrip('-')
        self.job_description = job_description
        self.responsive = False
        self.salary_upper = None
        self.salary_base = None
        self.job_type = None
        info_by_line = extra_info.strip().split("\n")
        last_line = info_by_line[-1]
        if last_line.startswith("Responded"):
            self.responsive = True
            prev_line = info_by_line[-2]
            if prev_line.startswith("$"):
                self.__parse_extras(prev_line)
        else:
            self.__parse_extras(last_line)

    def get_description(self) -> str:
        """
        Get just the description of a job object.
        :return:
        """
        return f"{self.job_description}"

    def get_overview(self) -> str:
        """
        Get a nicely formatted overview of all the available fields parsed from a job by the scraper.
        :return:
        """
        overview = f"Title: {self.title}\nCompany: {self.company} | Location: {self.location}\n"
        if self.salary_base is not None:
            overview += f"Salary base: {self.salary_base}\n"
        if self.salary_upper is not None:
            overview += f"Salary upper: {self.salary_upper}\n"
        if self.job_type is not None:
            overview += f"Job-Type: {self.job_type}"
        if self.responsive:
            overview += f"Responsive: {self.responsive}"
        return overview

    def as_dict(self) -> dict:
        """
        Method to convert a job obj to a dict for pandas
        :return:
        """
        return dict(
            title=self.title,
            company=self.company,
            location=self.location,
            job_description=self.job_description,
            is_responsive=self.responsive,
            salary_base=self.salary_base,
            salary_upper=self.salary_upper,
            job_type=self.job_type
        )
