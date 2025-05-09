import re
import datetime
import pytz


class DemoTextProcessingHelper:
    @staticmethod
    def remove_citations(sent):
        return (
            re.sub(r"\[\d+", "", re.sub(r" \[\d+", "", sent))
            .replace(" |", "")
            .replace("]", "")
        )

    @staticmethod
    def parse_conversation_history(json_data):
        """
        Given conversation log data, return list of parsed data of following format
        (persona_name, persona_description, list of dialogue turn)
        """
        parsed_data = []
        for persona_conversation_data in json_data:
            if ": " in persona_conversation_data["perspective"]:
                name, description = persona_conversation_data["perspective"].split(
                    ": ", 1
                )
            elif "- " in persona_conversation_data["perspective"]:
                name, description = persona_conversation_data["perspective"].split(
                    "- ", 1
                )
            else:
                name, description = "", persona_conversation_data["perspective"]
            cur_conversation = []
            for dialogue_turn in persona_conversation_data["dlg_turns"]:
                cur_conversation.append(
                    {"role": "user", "content": dialogue_turn["user_utterance"]}
                )
                cur_conversation.append(
                    {
                        "role": "assistant",
                        "content": DemoTextProcessingHelper.remove_citations(
                            dialogue_turn["agent_utterance"]
                        ),
                    }
                )
            parsed_data.append((name, description, cur_conversation))
        return parsed_data

    @staticmethod
    def parse(text):
        regex = re.compile(r']:\s+"(.*?)"\s+http')
        text = regex.sub("]: http", text)
        return text

    @staticmethod
    def add_markdown_indentation(input_string):
        lines = input_string.split("\n")
        processed_lines = [""]
        for line in lines:
            num_hashes = 0
            for char in line:
                if char == "#":
                    num_hashes += 1
                else:
                    break
            num_hashes -= 1
            num_spaces = 4 * num_hashes
            new_line = " " * num_spaces + line
            processed_lines.append(new_line)
        return "\n".join(processed_lines)

    @staticmethod
    def get_current_time_string():
        """
        Returns the current time in the California time zone as a string.

        Returns:
            str: The current California time in 'YYYY-MM-DD HH:MM:SS' format.
        """
        california_tz = pytz.timezone("America/Los_Angeles")
        utc_now = datetime.datetime.now(datetime.timezone.utc)
        california_now = utc_now.astimezone(california_tz)
        return california_now.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def compare_time_strings(
        time_string1, time_string2, time_format="%Y-%m-%d %H:%M:%S"
    ):
        """
        Compares two time strings to determine if they represent the same point in time.

        Args:
            time_string1 (str): The first time string to compare.
            time_string2 (str): The second time string to compare.
            time_format (str): The format of the time strings, defaults to '%Y-%m-%d %H:%M:%S'.

        Returns:
            bool: True if the time strings represent the same time, False otherwise.
        """
        # Parse the time strings into datetime objects
        time1 = datetime.datetime.strptime(time_string1, time_format)
        time2 = datetime.datetime.strptime(time_string2, time_format)

        # Compare the datetime objects
        return time1 == time2

    @staticmethod
    def add_inline_citation_link(article_text, citation_dict):
        # Regular expression to find citations like [i]
        pattern = r"\[(\d+)\]"

        # Function to replace each citation with its Markdown link
        def replace_with_link(match):
            i = match.group(1)
            url = citation_dict.get(int(i), {}).get("url", "#")
            return f"[[{i}]]({url})"

        # Replace all citations in the text with Markdown links
        return re.sub(pattern, replace_with_link, article_text)

    @staticmethod
    def generate_html_toc(md_text):
        toc = []
        for line in md_text.splitlines():
            if line.startswith("#"):
                level = line.count("#")
                title = line.strip("# ").strip()
                anchor = title.lower().replace(" ", "-").replace(".", "")
                toc.append(
                    f"<li style='margin-left: {20 * (level - 1)}px;'><a href='#{anchor}'>{title}</a></li>"
                )
        return "<ul>" + "".join(toc) + "</ul>"

    @staticmethod
    def construct_bibliography_from_url_to_info(url_to_info):
        bibliography_list = []
        sorted_url_to_unified_index = dict(
            sorted(
                url_to_info["url_to_unified_index"].items(), key=lambda item: item[1]
            )
        )
        for url, index in sorted_url_to_unified_index.items():
            title = url_to_info["url_to_info"][url]["title"]
            bibliography_list.append(f"[{index}]: [{title}]({url})")
        bibliography_string = "\n\n".join(bibliography_list)
        return f"# References\n\n{bibliography_string}"
