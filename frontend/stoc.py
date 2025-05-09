"""https://github.com/arnaudmiribel/stoc"""

import re

import streamlit as st
import unidecode

from knowledge_storm.dataclass import KnowledgeBase

DISABLE_LINK_CSS = """
<style>
a.toc {
    color: inherit;
    text-decoration: none; /* no underline */
}
</style>"""


class stoc:
    def __init__(self):
        self.toc_items = list()

    def h1(self, text: str, write: bool = False):
        if write:
            st.write(f"# {text}")
        self.toc_items.append(("h1", text))

    def h2(self, text: str, write: bool = False):
        if write:
            st.write(f"## {text}")
        self.toc_items.append(("h2", text))

    def h3(self, text: str, write: bool = False):
        if write:
            st.write(f"### {text}")
        self.toc_items.append(("h3", text))

    def toc(self):
        st.write(DISABLE_LINK_CSS, unsafe_allow_html=True)
        markdown_toc = ""
        for title_size, title in self.toc_items:
            h = int(title_size.replace("h", ""))
            markdown_toc += (
                " " * 2 * h
                + "- "
                + f'<a href="#{normalize(title)}" class="toc"> {title}</a> \n'
            )
        # st.sidebar.write(markdown_toc, unsafe_allow_html=True)
        st.write(markdown_toc, unsafe_allow_html=True)

    @classmethod
    def get_toc(cls, markdown_text: str, topic=""):
        def increase_heading_depth_and_add_top_heading(markdown_text, new_top_heading):
            lines = markdown_text.splitlines()
            # Increase the depth of each heading by adding an extra '#'
            increased_depth_lines = [
                "#" + line if line.startswith("#") else line for line in lines
            ]
            # Add the new top-level heading at the beginning
            increased_depth_lines.insert(0, f"# {new_top_heading}")
            # Re-join the modified lines back into a single string
            modified_text = "\n".join(increased_depth_lines)
            return modified_text

        if topic:
            markdown_text = increase_heading_depth_and_add_top_heading(
                markdown_text, topic
            )
        toc = []
        for line in markdown_text.splitlines():
            if line.startswith("#"):
                # Remove the '#' characters and strip leading/trailing spaces
                heading_text = line.lstrip("#").strip()
                # Create slug (lowercase, spaces to hyphens, remove non-alphanumeric characters)
                slug = (
                    re.sub(r"[^a-zA-Z0-9\s-]", "", heading_text)
                    .lower()
                    .replace(" ", "-")
                )
                # Determine heading level for indentation
                level = line.count("#") - 1
                # Add to the table of contents
                toc.append("  " * level + f"- [{heading_text}](#{slug})")
        return "\n".join(toc)

    @classmethod
    def from_markdown(cls, text: str):
        self = cls()
        lines = text.splitlines()
        
        if (lines[0] == "# summary"):
            lines = lines[1:]
        
        for line in lines:
            if line.startswith("###"):
                self.h3(line[3:], write=False)
            elif line.startswith("##"):
                self.h2(line[2:], write=False)
            elif line.startswith("#"):
                self.h1(line[1:], write=False)

        # from_markdown used not end here but continue with what now is
        # render_article, which then ended by calling self.toc.
        # 
        # The old from_markdown is equivalent to:
        # from_markdown, render_article, toc

        return self
    
    @classmethod
    def from_knowledge_base(cls, kb: KnowledgeBase):
        self = cls()
        
        root = kb.root
        for h1 in root.children:
            self.h1(h1.name)
            for h2 in h1.children:
                self.h2(h2.name)
                for h3 in h2.children:
                    self.h3(h3.name)
        
        return self


def normalize(s):
    """
    Normalize titles as valid HTML ids for anchors
    >>> normalize("it's a test to spot how Things happ3n héhé")
    "it-s-a-test-to-spot-how-things-happ3n-h-h"
    """

    # Replace accents with "-"
    s_wo_accents = unidecode.unidecode(s)
    accents = [s for s in s if s not in s_wo_accents]
    for accent in accents:
        s = s.replace(accent, "-")

    # Lowercase
    s = s.lower()

    # Keep only alphanum and remove "-" suffix if existing
    normalized = (
        "".join([char if char.isalnum() else "-" for char in s]).strip("-").lower()
    )

    return normalized
