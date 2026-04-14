#!/usr/bin/env python3
import os
from pathlib import Path

def get_department_info(dept_folder):
    """Get department display info"""
    dept_info = {
        'academic': {'name': 'Academic', 'emoji': '🎓', 'color': 'emerald', 'description': 'Stručnjaci za akademska istraživanja i analize'},
        'design': {'name': 'Design', 'emoji': '🎨', 'color': 'purple', 'description': 'UI/UX dizajn i vizuelne komunikacije'},
        'engineering': {'name': 'Engineering', 'emoji': '💻', 'color': 'cyan', 'description': 'Razvoj softvera i tehnička implementacija'},
        'finance': {'name': 'Finance', 'emoji': '💰', 'color': 'green', 'description': 'Finansijsko upravljanje i analiza'},
        'game-development': {'name': 'Game Development', 'emoji': '🎮', 'color': 'red', 'description': 'Razvoj igara i interaktivni entertainment'},
        'marketing': {'name': 'Marketing', 'emoji': '📈', 'color': 'blue', 'description': 'Digitalni marketing i rast biznisa'},
        'paid-media': {'name': 'Paid Media', 'emoji': '💸', 'color': 'yellow', 'description': 'Plačene medijske kampanje i advertising'},
        'product': {'name': 'Product', 'emoji': '🚀', 'color': 'indigo', 'description': 'Product management i strategija'},
        'project-management': {'name': 'Project Management', 'emoji': '📋', 'color': 'blue', 'description': 'Upravljanje projektima i koordinacija'},
        'sales': {'name': 'Sales', 'emoji': '🎯', 'color': 'orange', 'description': 'Prodaja i poslovni razvoj'},
        'spatial-computing': {'name': 'Spatial Computing', 'emoji': '🌐', 'color': 'teal', 'description': 'Prostorno računarstvo i XR tehnologije'},
        'specialized': {'name': 'Specialized', 'emoji': '🔧', 'color': 'gray', 'description': 'Specijalizovani servisi i ekspertiza'},
        'support': {'name': 'Support', 'emoji': '🛠️', 'color': 'slate', 'description': 'Tehnička podrška i korisnički servis'},
        'testing': {'name': 'Testing', 'emoji': '🧪', 'color': 'orange', 'description': 'Kvalitet i testiranje softvera'}
    }
    return dept_info.get(dept_folder, {'name': dept_folder.title(), 'emoji': '🤖', 'color': 'slate', 'description': f'{dept_folder.title()} specijalisti'})

def generate_department_cards():
    """Generate HTML cards for all departments"""
    base_path = Path('/workspaces/agency-agents-njs')
    departments = [
        'academic', 'design', 'engineering', 'finance', 'game-development',
        'marketing', 'paid-media', 'product', 'project-management', 'sales',
        'spatial-computing', 'specialized', 'support', 'testing'
    ]

    cards = []
    for dept in departments:
        info = get_department_info(dept)
        dept_path = base_path / dept
        if dept == 'game-development':
            dept_path = base_path / 'game-development'

        # Count agents
        agent_count = 0
        if dept_path.exists():
            for file in dept_path.glob('*.md'):
                agent_count += 1
        if dept == 'game-development':
            # Count agents in subfolders
            for subfolder in ['godot', 'roblox-studio', 'unity', 'unreal-engine']:
                sub_path = base_path / 'game-development' / subfolder
                if sub_path.exists():
                    for file in sub_path.glob('*.md'):
                        agent_count += 1

        card = f'''          <article class="group rounded-3xl border border-slate-200/80 bg-white/90 p-6 shadow-soft backdrop-blur-xl transition hover:shadow-lg dark:border-slate-800/80 dark:bg-slate-900/80">
            <div class="flex items-center gap-4 mb-4">
              <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-{info['color']}-100 dark:bg-{info['color']}-500/20">
                <span class="text-2xl">{info['emoji']}</span>
              </div>
              <div>
                <h3 class="text-xl font-semibold text-slate-900 dark:text-slate-100">{info['name']}</h3>
                <p class="text-sm text-slate-600 dark:text-slate-400">{agent_count} agenata</p>
              </div>
            </div>
            <p class="mb-6 text-slate-600 dark:text-slate-300">{info['description']}.</p>
            <a href="{dept}.html" class="inline-flex items-center gap-2 text-sm font-semibold text-brand-600 transition hover:text-brand-500 dark:text-brand-400">
              Pogledaj agente
              <svg class="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M9 18l6-6-6-6" />
              </svg>
            </a>
          </article>'''

        cards.append(card)

    return '\n'.join(cards)

def update_departments_html():
    """Update departments.html with all department cards"""
    cards_html = generate_department_cards()

    # Read current departments.html
    with open('/workspaces/agency-agents-njs/departments.html', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the main grid and replace content
    start_marker = '<main class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">'
    end_marker = '</main>'

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx) + len(end_marker)

    if start_idx != -1 and end_idx != -1:
        new_content = content[:start_idx + len(start_marker)] + '\n' + cards_html + '\n        ' + content[end_idx - len(end_marker):end_idx]

        with open('/workspaces/agency-agents-njs/departments.html', 'w', encoding='utf-8') as f:
            f.write(new_content)

        print("Updated departments.html with all departments")

if __name__ == '__main__':
    update_departments_html()