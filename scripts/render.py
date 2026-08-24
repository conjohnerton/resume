#!/usr/bin/env python3
"""Render resume.json into Markdown or LaTeX.

resume.json is the single source of truth. It follows the JSON Resume v1 schema.
Run this script with --format md or --format tex.
"""

import argparse
import json
import pathlib
import sys

MONTHS = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December",
}

TEX_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def month_year(value):
    """Turn 2023-01 into January 2023. Return Present for an empty value."""
    if not value:
        return "Present"
    parts = value.split("-")
    if len(parts) < 2:
        return parts[0]
    return f"{MONTHS[parts[1]]} {parts[0]}"


def date_range(start, end):
    return f"{month_year(start)} - {month_year(end)}"


def tex(text):
    """Escape a plain string for LaTeX."""
    out = []
    for char in str(text):
        out.append(TEX_ESCAPES.get(char, char))
    return "".join(out)


def strip_scheme(url):
    for prefix in ("https://", "http://"):
        if url.startswith(prefix):
            return url[len(prefix):]
    return url


# --------------------------------------------------------------------------- #
# Markdown
# --------------------------------------------------------------------------- #

def render_markdown(data):
    basics = data["basics"]
    lines = [f"# {basics['name']}", ""]

    contact = []
    region = basics.get("location", {}).get("region")
    if region:
        contact.append(region)
    if basics.get("email"):
        contact.append(f"[{basics['email']}](mailto:{basics['email']})")
    if basics.get("url"):
        contact.append(f"[{strip_scheme(basics['url'])}]({basics['url']})")
    lines += [" · ".join(contact), ""]

    if data.get("work"):
        lines += ["## Experience", ""]
        for job in data["work"]:
            span = date_range(job.get("startDate"), job.get("endDate"))
            head = f"### {job['name']}"
            if job.get("location"):
                head += f" · {job['location']}"
            lines.append(head)
            lines.append(f"*{job['position']}* · *{span}*")
            lines.append("")
            for point in job.get("highlights", []):
                lines.append(f"- {point}")
            lines.append("")

    if data.get("awards"):
        lines += ["## Recognition", ""]
        for award in data["awards"]:
            when = month_year(award.get("date"))
            lines.append(f"### {award['title']}")
            awarder = award.get("awarder", "")
            lines.append(f"*{awarder}* · *{when}*")
            if award.get("summary"):
                lines.append("")
                lines.append(award["summary"])
            lines.append("")

    if data.get("projects"):
        lines += ["## Projects", ""]
        for project in data["projects"]:
            stack = ", ".join(project.get("keywords", []))
            head = f"### {project['name']}"
            if stack:
                head += f" \u00b7 {stack}"
            lines.append(head)
            if project.get("url"):
                lines.append(f"[{strip_scheme(project['url'])}]({project['url']})")
                lines.append("")
            lines.append(project.get("description", ""))
            lines.append("")

    if data.get("education"):
        lines += ["## Education", ""]
        for school in data["education"]:
            span = date_range(school.get("startDate"), school.get("endDate"))
            lines.append(f"### {school['institution']}")
            degree = f"{school.get('studyType', '')} {school.get('area', '')}".strip()
            if school.get("score"):
                degree += f", GPA: {school['score']}"
            lines.append(f"*{degree}* \u00b7 *{span}*")
            lines.append("")

    if data.get("skills"):
        lines += ["## Skills", ""]
        for group in data["skills"]:
            lines.append(f"- **{group['name']}:** {', '.join(group.get('keywords', []))}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


# --------------------------------------------------------------------------- #
# LaTeX
# --------------------------------------------------------------------------- #

def render_latex(data, template):
    basics = data["basics"]
    body = []

    def entry(left, right, sub_left, sub_right):
        body.append(
            "\\entry{%s}{%s}{%s}{%s}" % (tex(left), tex(right), tex(sub_left), tex(sub_right))
        )

    def bullets(points):
        body.append("\\begin{itemize}")
        for point in points:
            body.append("  \\item %s" % tex(point))
        body.append("\\end{itemize}")

    if data.get("work"):
        body.append("\\section*{Experience}")
        for job in data["work"]:
            entry(
                job["name"],
                job.get("location", ""),
                job["position"],
                date_range(job.get("startDate"), job.get("endDate")),
            )
            bullets(job.get("highlights", []))

    if data.get("awards"):
        body.append("\\section*{Recognition}")
        for award in data["awards"]:
            entry(
                award["title"],
                month_year(award.get("date")),
                award.get("summary", ""),
                "",
            )

    if data.get("projects"):
        body.append("\\section*{Projects}")
        for project in data["projects"]:
            stack = ", ".join(project.get("keywords", []))
            if stack:
                stack = " $\\cdot$ \\textit{%s}" % tex(stack)
            link = ""
            if project.get("url"):
                link = "\\href{%s}{%s}" % (project["url"], tex(strip_scheme(project["url"])))
            body.append(
                "\\projectentry{%s}{%s}{%s}" % (tex(project["name"]), stack, link)
            )
            body.append(tex(project.get("description", "")))
            body.append("")

    if data.get("education"):
        body.append("\\section*{Education}")
        for school in data["education"]:
            degree = f"{school.get('studyType', '')} {school.get('area', '')}".strip()
            if school.get("score"):
                degree += f", GPA: {school['score']}"
            entry(
                school["institution"],
                "",
                degree,
                date_range(school.get("startDate"), school.get("endDate")),
            )

    if data.get("skills"):
        body.append("\\section*{Skills}")
        body.append("\\begin{skilllist}")
        for group in data["skills"]:
            body.append(
                "  \\item[\\textbf{%s:}] %s"
                % (tex(group["name"]), tex(", ".join(group.get("keywords", []))))
            )
        body.append("\\end{skilllist}")

    contact = []
    region = basics.get("location", {}).get("region")
    if region:
        contact.append(tex(region))
    if basics.get("email"):
        contact.append("\\href{mailto:%s}{%s}" % (basics["email"], tex(basics["email"])))
    if basics.get("url"):
        contact.append(
            "\\href{%s}{%s}" % (basics["url"], tex(strip_scheme(basics["url"])))
        )

    return (
        template.replace("<<NAME>>", tex(basics["name"]))
        .replace("<<CONTACT>>", " $\\cdot$ ".join(contact))
        .replace("<<BODY>>", "\n".join(body))
    )


# --------------------------------------------------------------------------- #

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description="Render resume.json")
    parser.add_argument("--format", required=True, choices=["md", "tex"])
    parser.add_argument("--input", default=str(root / "resume.json"))
    parser.add_argument("--output", help="Output file. Defaults to stdout.")
    args = parser.parse_args()

    data = json.loads(pathlib.Path(args.input).read_text(encoding="utf-8"))

    if args.format == "md":
        result = render_markdown(data)
    else:
        template = (root / "templates" / "resume.tex.template").read_text(encoding="utf-8")
        result = render_latex(data, template)

    if args.output:
        pathlib.Path(args.output).write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
