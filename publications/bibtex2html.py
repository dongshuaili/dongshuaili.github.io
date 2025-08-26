import bibtexparser
import codecs
import latexcodec
import re
from collections import defaultdict

# def latex_to_unicode(s: str) -> str:
#     if not s:
#         return ""
#     return codecs.decode(s.encode("utf-8"), "latex")

def latex_to_unicode(s: str) -> str:
    if not s:
        return ""
    # Safe version: only remove braces, leave UTF-8 chars
    return re.sub(r"[{}]", "", s)

def clean_braces(s: str) -> str:
    if not s:
        return ""
    return re.sub(r"[{}]", "", s)

# def format_authors(authors_str: str) -> str:
#     authors = [a.strip() for a in authors_str.split(" and ")]
#     formatted = []
#     for a in authors:
#         if "," in a:
#             last, first = [x.strip() for x in a.split(",", 1)]
#         else:
#             parts = a.split()
#             last, first = parts[-1], " ".join(parts[:-1])
#         initials = "".join([p[0] + "." for p in first.split() if p])
#         formatted.append(f"{last}, {initials}")
#     if len(formatted) > 1:
#         return ", ".join(formatted[:-1]) + " and " + formatted[-1]
#     return formatted[0]

def format_authors_full(authors_str: str, bold_name="Li, Dongshuai") -> str:
    """
    Format authors as: Last, First Middle; ... ; and Last, First Middle
    Bold the target author.
    """
    authors = [a.strip() for a in authors_str.split(" and ")]
    if len(authors) == 1:
        return f"<strong>{authors[0]}</strong>" if authors[0] == bold_name else authors[0]

    formatted = []
    for a in authors[:-1]:
        if "," in a:
            last, first = [x.strip() for x in a.split(",", 1)]
        else:
            parts = a.split()
            last, first = parts[-1], " ".join(parts[:-1])
        name_str = f"{last}, {first}"
        if name_str == bold_name:
            name_str = f"<strong>{name_str}</strong>"
        formatted.append(name_str)

    # Last author with 'and'
    last = authors[-1]
    if "," in last:
        last_last, last_first = [x.strip() for x in last.split(",", 1)]
    else:
        parts = last.split()
        last_last, last_first = parts[-1], " ".join(parts[:-1])
    last_name_str = f"{last_last}, {last_first}"
    if last_name_str == bold_name:
        last_name_str = f"<strong>{last_name_str}</strong>"
    formatted.append(f"and {last_name_str}")

    # Join using semicolons
    return "; ".join(formatted)

def format_entry(entry):
    authors = format_authors_full(clean_braces(latex_to_unicode(entry.get("author", ""))))

    # Extract year only
    date_field = entry.get("date", "") or entry.get("year", "")
    year_match = re.search(r"\d{4}", date_field)
    year = year_match.group(0) if year_match else ""

    title = clean_braces(latex_to_unicode(entry.get("title", "")))
    journal = clean_braces(latex_to_unicode(entry.get("journaltitle", "")))
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")
    doi = entry.get("doi", "")

    # Start citation
    citation = f"{authors}, {year}. {title}. <em>{journal}</em>"

    # Add volume/number/pages without extra commas
    if volume:
        citation += f", {volume}"
        if number:
            citation += f"({number})"
    if pages:
        citation += f", {pages}"
    if doi:
        doi_url = doi
        if not doi.lower().startswith("http"):
            doi_url = f"https://doi.org/{doi}"
        citation += f", <a href='{doi_url}' target='_blank' class='text-blue-600 hover:underline'>{doi_url}</a>"

    # citation += "."
    return citation, year

# --- Load BibTeX ---
with open("publications.bib") as bibtex_file:
    bib_database = bibtexparser.load(bibtex_file)

# --- Group entries by year ---
by_year = defaultdict(list)
for e in bib_database.entries:
    citation, year = format_entry(e)
    by_year[year].append(citation)

sorted_years = sorted(by_year.keys(), reverse=True)

# --- Write HTML ---
with open("index.html", "w", encoding="utf-8") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Publications</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 text-gray-800 font-sans leading-relaxed">
  <div class="max-w-5xl mx-auto px-6 py-12">
""")

    # --- Book Chapters ---
    f.write("""
    <h1 class="text-4xl font-extrabold mb-12 text-center text-gray-900">Book Chapters</h1>
    <div class="space-y-6 mb-12">

    <div class="bg-white shadow-lg rounded-2xl p-6 hover:shadow-xl transition duration-300 ease-in-out">
        <p class="text-gray-800 text-base md:text-lg leading-relaxed">
        <strong>Dongshuai Li</strong>, Alejandro Luque, Farhad Rachidi, Marcos Rubinstein, 2022<br>
        <em>Advanced Time Domain Modelling for Electrical Engineering</em><br>
        Chapter 11: <span class="font-medium">The Application of The Finite-Difference Time-Domain (FDTD) Technique to Lightning Studies</span><br>
        The Institution of Engineering and Technology (IET)<br>
        <span class="text-sm">ISBN: 9781839531538 | <a href="https://doi.org/10.1049/SBEW550E_ch11" target="_blank" class="text-blue-600 hover:underline">https://doi.org/10.1049/SBEW550E_ch11</a></span>
        </p>
    </div>

    <div class="bg-white shadow-lg rounded-2xl p-6 hover:shadow-xl transition duration-300 ease-in-out">
        <p class="text-gray-800 text-base md:text-lg leading-relaxed">
        <strong>Dongshuai Li</strong>, Alejandro Luque, Marcos Rubinstein, Farhad Rachidi, 2023<br>
        <em>Lightning Electromagnetics, 2nd Edition</em><br>
        Chapter 10: <span class="font-medium">Lightning interaction with the ionosphere</span><br>
        The Institution of Engineering and Technology (IET)<br>
        <span class="text-sm">ISBN: 9781785615412 | <a href="https://doi.org/10.1049/PBPO127G_ch10" target="_blank" class="text-blue-600 hover:underline">https://doi.org/10.1049/PBPO127G_ch10</a></span>
        </p>
    </div>

    </div>
    """)


    # --- Journal Publications ---
    f.write("""
    <h1 class="text-4xl font-extrabold mb-12 text-center text-gray-900">Journal Publications</h1>
""")
    for year in sorted_years:
        f.write(f"""
        <div class="mb-12">
          <h2 class="text-3xl font-semibold mb-6 border-b-2 border-gray-300 pb-2">{year}</h2>
          <div class="space-y-6">
        """)
        for c in by_year[year]:
            f.write(f"""
            <div class="bg-white shadow-lg rounded-2xl p-6 hover:shadow-xl transition duration-300 ease-in-out">
              <p class="text-gray-800 text-base md:text-lg leading-relaxed">{c}</p>
            </div>
            """)
        f.write("</div></div>")

    f.write("""
  </div>
</body>
</html>
""")


