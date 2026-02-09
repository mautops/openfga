# AGENTS

<skills_system priority="1">

## Available Skills

<!-- SKILLS_TABLE_START -->
<usage>
When users ask you to perform tasks, check if any of the available skills below can help complete the task more effectively. Skills provide specialized capabilities and domain knowledge.

How to use skills:
- Invoke: Bash("openskills read <skill-name>")
- The skill content will load with detailed instructions on how to complete the task
- Base directory provided in output for resolving bundled resources (references/, scripts/, assets/)

Usage notes:
- Only use skills listed in <available_skills> below
- Do not invoke a skill that is already loaded in your context
- Each skill invocation is stateless
</usage>

<available_skills>

<skill>
<name>teck-world-book</name>
<description>专业的计算机技术类电子书撰写助手。当用户需要撰写技术书籍、编程教程、技术文档或计算机相关的教学材料时使用。支持完整的书籍结构设计、章节内容撰写、代码示例编写、练习题设计等。特别注重去除 AI 写作痕迹，使内容更加自然、有个性，符合真实技术作者的写作风格。适用于 Python、JavaScript、Go、Java 等各类编程语言和技术栈的书籍创作。</description>
<location>global</location>
</skill>

</available_skills>
<!-- SKILLS_TABLE_END -->

</skills_system>
