#!/usr/bin/env python3
import os
from pathlib import Path

def parse_md_file(filepath):
    """Parse a markdown file with frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Split frontmatter and content
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_text = parts[1]
            body = parts[2].strip()

            # Parse frontmatter manually
            frontmatter = {}
            lines = frontmatter_text.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    frontmatter[key] = value

            return frontmatter
    return None

def get_color_class(color):
    """Convert color name to Tailwind class"""
    color_map = {
        'cyan': 'cyan',
        'purple': 'purple',
        'blue': 'blue',
        'green': 'green',
        'red': 'red',
        'yellow': 'yellow',
        'pink': 'pink',
        'indigo': 'indigo',
        'teal': 'teal',
        'orange': 'orange',
        'gray': 'gray',
        'slate': 'slate',
        'emerald': 'emerald'
    }
    return color_map.get(color, 'slate')

def get_department_display_name(folder_name):
    """Convert folder name to display name"""
    name_map = {
        'academic': 'Academic',
        'design': 'Design',
        'engineering': 'Engineering',
        'finance': 'Finance',
        'game-development': 'Game Development',
        'marketing': 'Marketing',
        'paid-media': 'Paid Media',
        'product': 'Product',
        'project-management': 'Project Management',
        'sales': 'Sales',
        'spatial-computing': 'Spatial Computing',
        'specialized': 'Specialized',
        'support': 'Support',
        'testing': 'Testing'
    }
    return name_map.get(folder_name, folder_name.replace('-', ' ').title())

def generate_agent_sections():
    """Generate HTML sections for all agents grouped by department"""
    base_path = Path('/workspaces/agency-agents-njs')
    departments = [
        'academic', 'design', 'engineering', 'finance', 'game-development',
        'marketing', 'paid-media', 'product', 'project-management', 'sales',
        'spatial-computing', 'specialized', 'support', 'testing'
    ]

    sections = []
    for dept in departments:
        dept_display = get_department_display_name(dept)
        agents = []

        # Handle game-development specially
        if dept == 'game-development':
            # Main game-development folder
            dept_path = base_path / dept
            if dept_path.exists():
                for md_file in dept_path.glob('*.md'):
                    frontmatter = parse_md_file(md_file)
                    if frontmatter:
                        frontmatter['filename'] = md_file.name
                        agents.append(frontmatter)

            # Subfolders
            for subfolder in ['godot', 'roblox-studio', 'unity', 'unreal-engine']:
                sub_path = base_path / dept / subfolder
                if sub_path.exists():
                    for md_file in sub_path.glob('*.md'):
                        frontmatter = parse_md_file(md_file)
                        if frontmatter:
                            frontmatter['filename'] = md_file.name
                            agents.append(frontmatter)
        else:
            dept_path = base_path / dept
            if dept_path.exists():
                for md_file in dept_path.glob('*.md'):
                    frontmatter = parse_md_file(md_file)
                    if frontmatter:
                        frontmatter['filename'] = md_file.name
                        agents.append(frontmatter)

        if not agents:
            continue

        # Sort agents by name
        agents.sort(key=lambda x: x['name'])

        # Generate agent cards
        agent_cards = []
        for agent in agents:
            color_class = get_color_class(agent.get('color', 'slate'))
            emoji = agent.get('emoji', '🤖')
            name = agent['name']
            description = agent['description'][:80] + '...' if len(agent['description']) > 80 else agent['description']
            filename = agent['filename'].replace('.md', '.html')

            card = f'''              <article class="group rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl transition hover:shadow-lg dark:border-slate-800/80 dark:bg-slate-900/80">
                <div class="flex items-start gap-4 mb-4">
                  <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-{color_class}-100 dark:bg-{color_class}-500/20">
                    <span class="text-2xl">{emoji}</span>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-lg font-semibold text-slate-900 dark:text-slate-100">{name}</h3>
                    <p class="text-sm text-slate-600 dark:text-slate-400">{description}</p>
                  </div>
                  <span class="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300">Available</span>
                </div>
                <a href="{filename}" class="inline-flex items-center gap-2 text-sm font-semibold text-brand-600 transition hover:text-brand-500 dark:text-brand-400">
                  Detalji
                  <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M9 18l6-6-6-6" />
                  </svg>
                </a>
              </article>'''
            agent_cards.append(card)

        section = f'''
          <section>
            <h2 class="mb-6 text-2xl font-semibold">{dept_display}</h2>
            <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
{chr(10).join(agent_cards)}
            </div>
          </section>'''

        sections.append(section)

    return '\n'.join(sections)

def update_agents_html():
    """Update agents.html with all agents"""
    sections_html = generate_agent_sections()

    # Read current agents.html
    with open('/workspaces/agency-agents-njs/agents.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the main content area and replace everything between <main> and </main>
    main_start = content.find('<main')
    main_end = content.find('</main>', main_start) + 7

    if main_start != -1 and main_end != -1:
        # Extract header and footer
        header = content[:main_start]
        footer_start = content.find('<script', main_end)
        if footer_start == -1:
            footer_start = main_end
        footer = content[footer_start:]

        # Create new main content
        new_main = '''        <main class="space-y-12">
''' + sections_html + '''
        </main>'''

        new_content = header + new_main + footer

        with open('/workspaces/agency-agents-njs/agents.html', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Updated agents.html with all agents")

if __name__ == '__main__':
    update_agents_html()