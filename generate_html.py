#!/usr/bin/env python3
import os
import yaml
import re
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

            # Parse frontmatter manually since YAML has issues with complex strings
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

            return frontmatter, body
    return None, content

def get_department_name(folder_name):
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
        'gray': 'gray'
    }
    return color_map.get(color, 'slate')

def generate_department_page(department, agents):
    """Generate HTML for a department page"""
    dept_name = get_department_name(department)

    # Sort agents by name
    agents.sort(key=lambda x: x['name'])

    agent_cards = []
    for agent in agents:
        color_class = get_color_class(agent.get('color', 'slate'))
        emoji = agent.get('emoji', '🤖')
        name = agent['name']
        description = agent['description'][:100] + '...' if len(agent['description']) > 100 else agent['description']
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

    html = f'''<!DOCTYPE html>
<html lang="sr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{dept_name} Department</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {{
        darkMode: 'class',
        theme: {{
          extend: {{
            boxShadow: {{
              soft: '0 20px 60px rgba(15, 23, 42, 0.08)',
            }},
            colors: {{
              brand: {{
                500: '#5c6ac4',
                600: '#4f57b0',
              }},
            }},
          }},
        }},
      }};
    </script>
    <style>
      body {{
        transition: background-color 0.3s ease, color 0.3s ease;
      }}
      .theme-icon {{
        width: 1.35rem;
        height: 1.35rem;
      }}
    </style>
  </head>
  <body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <div class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <header class="mb-8 flex flex-col gap-6 rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
          <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-brand-600 dark:text-brand-400">{dept_name} Department</p>
              <h1 class="mt-4 text-3xl font-semibold sm:text-4xl">🚀 {dept_name} Odeljenje</h1>
              <p class="mt-3 max-w-2xl text-slate-600 dark:text-slate-300">Stručnjaci u {dept_name.lower()} oblasti koji pružaju vrhunske usluge i rešenja za vaše potrebe.</p>
            </div>
            <button id="theme-toggle" aria-label="Toggle theme" class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200/90 bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-200 dark:border-slate-700/90 dark:bg-slate-800 dark:text-slate-100 dark:hover:border-slate-600">
              <svg class="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path id="theme-sun" class="hidden" d="M12 3v2M12 19v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 7a5 5 0 100 10 5 5 0 000-10z" />
                <path id="theme-moon" d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" />
              </svg>
              <span id="theme-label">Dark mode</span>
            </button>
          </div>
          <nav class="flex flex-wrap gap-2">
            <a href="index.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Dashboard</a>
            <a href="departments.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Odeljenja</a>
            <a href="agents.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Svi agenti</a>
            <a href="{department}.html" class="rounded-full bg-brand-600 px-4 py-2 text-sm font-medium text-white">{dept_name}</a>
          </nav>
        </header>

        <main class="space-y-8">
          <section>
            <h2 class="mb-6 text-2xl font-semibold">Naši {dept_name.lower()} specijalisti</h2>
            <div class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
{chr(10).join(agent_cards)}
            </div>
          </section>

          <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
            <h2 class="mb-4 text-2xl font-semibold">O {dept_name} odeljenju</h2>
            <p class="mb-6 text-slate-600 dark:text-slate-300">Naše {dept_name.lower()} odeljenje okuplja vrhunske stručnjake koji pružaju inovativna rešenja i ekspertizu u svojoj oblasti. Svaki član tima donosi jedinstvenu perspektivu i duboko znanje koje pomaže klijentima da postignu svoje ciljeve.</p>

            <div class="grid gap-6 md:grid-cols-3">
              <div class="text-center">
                <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-{color_class}-100 dark:bg-{color_class}-500/20">
                  <span class="text-3xl">🎯</span>
                </div>
                <h3 class="mb-2 font-semibold text-slate-900 dark:text-slate-100">Expertise</h3>
                <p class="text-sm text-slate-600 dark:text-slate-400">Duboko znanje i iskustvo u {dept_name.lower()} oblastima.</p>
              </div>

              <div class="text-center">
                <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-{color_class}-100 dark:bg-{color_class}-500/20">
                  <span class="text-3xl">🚀</span>
                </div>
                <h3 class="mb-2 font-semibold text-slate-900 dark:text-slate-100">Innovation</h3>
                <p class="text-sm text-slate-600 dark:text-slate-400">Najnovije tehnologije i pristupi za optimalna rešenja.</p>
              </div>

              <div class="text-center">
                <div class="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-{color_class}-100 dark:bg-{color_class}-500/20">
                  <span class="text-3xl">🤝</span>
                </div>
                <h3 class="mb-2 font-semibold text-slate-900 dark:text-slate-100">Collaboration</h3>
                <p class="text-sm text-slate-600 dark:text-slate-400">Timski rad i saradnja za postizanje izvanrednih rezultata.</p>
              </div>
            </div>
          </section>
        </main>
      </div>
    </div>

    <script>
      const themeToggle = document.getElementById('theme-toggle');
      const themeLabel = document.getElementById('theme-label');
      const sunIcon = document.getElementById('theme-sun');
      const moonIcon = document.getElementById('theme-moon');

      function setTheme(theme) {{
        const root = document.documentElement;
        if (theme === 'dark') {{
          root.classList.add('dark');
          themeLabel.textContent = 'Light mode';
          sunIcon.classList.remove('hidden');
          moonIcon.classList.add('hidden');
        }} else {{
          root.classList.remove('dark');
          themeLabel.textContent = 'Dark mode';
          moonIcon.classList.remove('hidden');
          sunIcon.classList.add('hidden');
        }}
      }}

      const savedTheme = localStorage.getItem('dashboard-theme');
      setTheme(savedTheme === 'dark' ? 'dark' : 'light');

      themeToggle.addEventListener('click', () => {{
        const isDark = document.documentElement.classList.contains('dark');
        const nextTheme = isDark ? 'light' : 'dark';
        setTheme(nextTheme);
        localStorage.setItem('dashboard-theme', nextTheme);
      }});
    </script>
  </body>
</html>'''

    return html

def generate_agent_page(agent_data, department):
    """Generate HTML for an individual agent page"""
    name = agent_data['name']
    description = agent_data['description']
    color = agent_data.get('color', 'slate')
    emoji = agent_data.get('emoji', '🤖')
    vibe = agent_data.get('vibe', '')
    body = agent_data.get('body', '')

    color_class = get_color_class(color)
    filename = agent_data['filename'].replace('.md', '.html')
    dept_name = get_department_name(department)

    # Extract some info from body for the page
    # This is a simple extraction - in reality might need more parsing
    skills = []
    if '## 🎯 Your Core Mission' in body:
        mission_section = body.split('## 🎯 Your Core Mission')[1].split('##')[0]
        # Extract bullet points as skills
        bullets = re.findall(r'- \*\*(.*?)\*\*', mission_section)
        skills = bullets[:6]  # Take first 6 skills

    html = f'''<!DOCTYPE html>
<html lang="sr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {{
        darkMode: 'class',
        theme: {{
          extend: {{
            boxShadow: {{
              soft: '0 20px 60px rgba(15, 23, 42, 0.08)',
            }},
            colors: {{
              brand: {{
                500: '#5c6ac4',
                600: '#4f57b0',
              }},
            }},
          }},
        }},
      }};
    </script>
    <style>
      body {{
        transition: background-color 0.3s ease, color 0.3s ease;
      }}
      .theme-icon {{
        width: 1.35rem;
        height: 1.35rem;
      }}
    </style>
  </head>
  <body class="bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
    <div class="min-h-screen px-4 py-6 sm:px-6 lg:px-8">
      <div class="mx-auto max-w-7xl">
        <header class="mb-8 flex flex-col gap-6 rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
          <div class="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <p class="text-sm font-semibold uppercase tracking-[0.3em] text-brand-600 dark:text-brand-400">{dept_name} Department</p>
              <h1 class="mt-4 text-3xl font-semibold sm:text-4xl">{emoji} {name}</h1>
              <p class="mt-3 max-w-2xl text-slate-600 dark:text-slate-300">{description}</p>
            </div>
            <button id="theme-toggle" aria-label="Toggle theme" class="inline-flex items-center justify-center gap-2 rounded-full border border-slate-200/90 bg-slate-100 px-4 py-3 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-200 dark:border-slate-700/90 dark:bg-slate-800 dark:text-slate-100 dark:hover:border-slate-600">
              <svg class="theme-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path id="theme-sun" class="hidden" d="M12 3v2M12 19v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42M12 7a5 5 0 100 10 5 5 0 000-10z" />
                <path id="theme-moon" d="M21 12.79A9 9 0 1111.21 3a7 7 0 109.79 9.79z" />
              </svg>
              <span id="theme-label">Dark mode</span>
            </button>
          </div>
          <nav class="flex flex-wrap gap-2">
            <a href="index.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Dashboard</a>
            <a href="departments.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Odeljenja</a>
            <a href="agents.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">Svi agenti</a>
            <a href="{department}.html" class="rounded-full bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700">{dept_name}</a>
          </nav>
        </header>

        <main class="space-y-8">
          <div class="grid gap-8 lg:grid-cols-3">
            <div class="lg:col-span-2 space-y-8">
              <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
                <h2 class="mb-6 text-2xl font-semibold">O meni</h2>
                <p class="mb-6 text-slate-600 dark:text-slate-300">{vibe}</p>

                <div class="grid gap-6 md:grid-cols-2">
                  <div>
                    <h3 class="mb-3 font-semibold text-slate-900 dark:text-slate-100">Ključne veštine</h3>
                    <ul class="space-y-2 text-sm text-slate-600 dark:text-slate-400">
{chr(10).join([f'                      <li>• {skill}</li>' for skill in skills])}
                    </ul>
                  </div>
                  <div>
                    <h3 class="mb-3 font-semibold text-slate-900 dark:text-slate-100">Tehnologije</h3>
                    <div class="flex flex-wrap gap-2">
                      <span class="rounded-full bg-{color_class}-100 px-3 py-1 text-xs font-medium text-{color_class}-700 dark:bg-{color_class}-500/20 dark:text-{color_class}-300">{name.split()[0]}</span>
                    </div>
                  </div>
                </div>
              </section>

              <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
                <h2 class="mb-6 text-2xl font-semibold">Nedavni projekti</h2>
                <div class="space-y-6">
                  <article class="border-b border-slate-200 pb-6 last:border-b-0 dark:border-slate-700">
                    <h3 class="mb-2 text-lg font-semibold text-slate-900 dark:text-slate-100">Projekt 1</h3>
                    <p class="mb-3 text-sm text-slate-600 dark:text-slate-400">Opis projekta i postignuti rezultati.</p>
                    <div class="flex flex-wrap gap-2">
                      <span class="rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-700 dark:bg-green-500/20 dark:text-green-300">Completed</span>
                    </div>
                  </article>
                </div>
              </section>
            </div>

            <div class="space-y-8">
              <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
                <h2 class="mb-6 text-2xl font-semibold">Status</h2>
                <div class="flex items-center gap-3 mb-4">
                  <div class="h-3 w-3 rounded-full bg-emerald-500"></div>
                  <span class="text-sm font-medium text-emerald-700 dark:text-emerald-300">Online</span>
                </div>
                <p class="text-sm text-slate-600 dark:text-slate-400">Dostupan za konsultacije.</p>
              </section>

              <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
                <h2 class="mb-6 text-2xl font-semibold">Kontakt</h2>
                <div class="space-y-4">
                  <div class="flex items-center gap-3">
                    <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-100 dark:bg-slate-800">
                      <svg class="h-4 w-4 text-slate-600 dark:text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-slate-900 dark:text-slate-100">{name.lower().replace(' ', '.')}@agency.com</p>
                      <p class="text-xs text-slate-500 dark:text-slate-400">Email</p>
                    </div>
                  </div>
                </div>
              </section>

              <section class="rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl dark:border-slate-800/80 dark:bg-slate-900/80">
                <h2 class="mb-6 text-2xl font-semibold">Statistike</h2>
                <div class="space-y-4">
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-slate-600 dark:text-slate-400">Završeni projekti</span>
                    <span class="text-sm font-semibold text-slate-900 dark:text-slate-100">25+</span>
                  </div>
                  <div class="flex justify-between items-center">
                    <span class="text-sm text-slate-600 dark:text-slate-400">Godine iskustva</span>
                    <span class="text-sm font-semibold text-slate-900 dark:text-slate-100">5+</span>
                  </div>
                </div>
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>

    <script>
      const themeToggle = document.getElementById('theme-toggle');
      const themeLabel = document.getElementById('theme-label');
      const sunIcon = document.getElementById('theme-sun');
      const moonIcon = document.getElementById('theme-moon');

      function setTheme(theme) {{
        const root = document.documentElement;
        if (theme === 'dark') {{
          root.classList.add('dark');
          themeLabel.textContent = 'Light mode';
          sunIcon.classList.remove('hidden');
          moonIcon.classList.add('hidden');
        }} else {{
          root.classList.remove('dark');
          themeLabel.textContent = 'Dark mode';
          moonIcon.classList.remove('hidden');
          sunIcon.classList.add('hidden');
        }}
      }}

      const savedTheme = localStorage.getItem('dashboard-theme');
      setTheme(savedTheme === 'dark' ? 'dark' : 'light');

      themeToggle.addEventListener('click', () => {{
        const isDark = document.documentElement.classList.contains('dark');
        const nextTheme = isDark ? 'light' : 'dark';
        setTheme(nextTheme);
        localStorage.setItem('dashboard-theme', nextTheme);
      }});
    </script>
  </body>
</html>'''

    return html

def main():
    base_path = Path('/workspaces/agency-agents-njs')
    departments = {}

    # Define department folders
    dept_folders = [
        'academic', 'design', 'engineering', 'finance', 'marketing',
        'paid-media', 'product', 'project-management', 'sales',
        'spatial-computing', 'specialized', 'support', 'testing'
    ]

    # Handle game-development separately
    game_agents = []
    game_folders = ['godot', 'roblox-studio', 'unity', 'unreal-engine']
    for subfolder in game_folders:
        folder_path = base_path / 'game-development' / subfolder
        if folder_path.exists():
            for md_file in folder_path.glob('*.md'):
                frontmatter, body = parse_md_file(md_file)
                if frontmatter:
                    frontmatter['filename'] = md_file.name
                    frontmatter['body'] = body
                    game_agents.append(frontmatter)

    # Add main game-development files
    game_main_path = base_path / 'game-development'
    for md_file in game_main_path.glob('*.md'):
        frontmatter, body = parse_md_file(md_file)
        if frontmatter:
            frontmatter['filename'] = md_file.name
            frontmatter['body'] = body
            game_agents.append(frontmatter)

    if game_agents:
        departments['game-development'] = game_agents

    # Process other departments
    for dept in dept_folders:
        dept_path = base_path / dept
        if dept_path.exists():
            agents = []
            for md_file in dept_path.glob('*.md'):
                frontmatter, body = parse_md_file(md_file)
                if frontmatter:
                    frontmatter['filename'] = md_file.name
                    frontmatter['body'] = body
                    agents.append(frontmatter)
            if agents:
                departments[dept] = agents

    # Generate department pages
    for dept, agents in departments.items():
        html_content = generate_department_page(dept, agents)
        output_file = base_path / f'{dept}.html'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f'Generated {dept}.html with {len(agents)} agents')

        # Generate individual agent pages
        for agent in agents:
            html_content = generate_agent_page(agent, dept)
            filename = agent['filename'].replace('.md', '.html')
            output_file = base_path / filename
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f'Generated {filename}')

if __name__ == '__main__':
    main()