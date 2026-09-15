using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;

namespace Nexus.Terminal;

public static class CommandParser
{
    public static (string Command, List<string> Args) Parse(string input)
    {
        if (string.IsNullOrWhiteSpace(input))
            return ("", new List<string>());

        input = input.Trim();
        var args = new List<string>();
        var regex = new Regex(@"""[^""]*""|'[^']*'|\S+");
        var matches = regex.Matches(input);

        if (matches.Count == 0)
            return ("", new List<string>());

        string command = matches[0].Value.Trim('"', '\'').ToLower();

        for (int i = 1; i < matches.Count; i++)
        {
            args.Add(matches[i].Value.Trim('"', '\''));
        }

        return (command, args);
    }

    public static List<string> ParseScriptLines(string scriptContent)
    {
        var lines = new List<string>();
        var rawLines = scriptContent.Split(new[] { "\r\n", "\r", "\n" }, StringSplitOptions.None);

        foreach (var line in rawLines)
        {
            string trimmed = line.Trim();
            if (!string.IsNullOrEmpty(trimmed) && !trimmed.StartsWith("#"))
            {
                lines.Add(trimmed);
            }
        }

        return lines;
    }

    public static bool IsAutocompleteCharacter(char c)
    {
        return c == '\t' || char.IsLetterOrDigit(c) || c == '.' || c == '/' || c == '\\' || c == '-' || c == '_';
    }
}
