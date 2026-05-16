from customtkinter import *
from tkinter import filedialog
from os import listdir, path, startfile
from threading import Thread
from multiprocessing import freeze_support
from PIL import Image

from img_reader import read_img

EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp', '.bmp'}
LINE_HEIGHT = 28
MAX_OUTPUT_LINES = 8
MAX_CODE_LINES = 20

folder = ''
images = []
current_file = ''


def set_text(textbox, text, max_lines=None):
    textbox.configure(state='normal')
    textbox.delete('1.0', 'end')
    textbox.insert('1.0', text)
    textbox.configure(state='disabled')
    if max_lines is not None:
        lines = max(text.count('\n') + 1, 1) if text else 1
        h = min(lines, max_lines) * LINE_HEIGHT + 16
        textbox.configure(height=h)


def clear_results():
    for box in (pseudo_box, python_box, output_box):
        set_text(box, '')
    output_title.configure(text='Saída', text_color='#bfbfbf')
    output_box.configure(text_color='#0f0')


def show_result(data):
    loading_label.pack_forget()
    run_btn.configure(state='normal')

    if 'error' in data:
        set_text(output_box, str(data['error']), MAX_OUTPUT_LINES)
        output_title.configure(text='Erro', text_color='#e74c3c')
        output_box.configure(text_color='#e74c3c')
        set_text(pseudo_box, '')
        set_text(python_box, '')
    else:
        set_text(pseudo_box, str(data.get('pseudocode', '')), MAX_CODE_LINES)
        set_text(python_box, str(data.get('python', '')), MAX_CODE_LINES)
        set_text(output_box, str(data.get('output', '')), MAX_OUTPUT_LINES)
        output_title.configure(text='Saída', text_color='#bfbfbf')
        output_box.configure(text_color='#0f0')


def run_processing(filepath):
    result = read_img(filepath)
    window.after(0, show_result, result)


def update_preview():
    global current_file
    if not current_file or not path.isfile(current_file):
        preview_btn.configure(image=None, text='Nenhuma\nimagem', state='disabled')
        return
    
    try:
        img = Image.open(current_file)
        img.thumbnail((160, 160))
        ctk_img = CTkImage(light_image=img, dark_image=img, size=img.size)
        preview_btn.configure(image=ctk_img, text='', state='normal')
    except Exception as e:
        preview_btn.configure(image=None, text='Erro', state='disabled')


def on_img_menu_change(selected):
    global current_file
    if selected == '—' or not folder:
        return
    current_file = path.join(folder, selected)
    update_preview()


def select_folder():
    global folder, images
    chosen = filedialog.askdirectory(title='Selecione a pasta com imagens')
    if not chosen:
        return

    found = sorted(
        f for f in listdir(chosen)
        if path.splitext(f)[1].lower() in EXTENSIONS
    )

    if not found:
        path_label.configure(text='Nenhuma imagem encontrada')
        img_menu.configure(values=['—'], state='disabled')
        img_menu.set('—')
        run_btn.configure(state='disabled')
        global current_file
        current_file = ''
        update_preview()
        return

    folder = chosen
    images = found
    path_label.configure(text=chosen)
    sel_row.pack(fill='x', padx=16, pady=(10, 0))
    img_menu.configure(values=found, state='normal')
    img_menu.set(found[0])
    
    current_file = path.join(folder, found[0])
    update_preview()
    
    run_btn.configure(state='normal')


def select_image():
    global folder, images, current_file
    filetypes = [('Imagens', ' '.join(f'*{e}' for e in EXTENSIONS))]
    filepath = filedialog.askopenfilename(
        title='Selecione uma imagem', filetypes=filetypes
    )
    if not filepath:
        return

    folder = ''
    images = []
    current_file = filepath
    update_preview()
    path_label.configure(text=path.basename(filepath))
    sel_row.pack_forget()
    clear_results()
    loading_label.pack(pady=(6, 0))
    Thread(target=run_processing, args=(filepath,), daemon=True).start()


def process():
    global current_file
    selected = img_menu.get()
    if selected == '—' or not folder:
        return

    current_file = path.join(folder, selected)
    update_preview()

    run_btn.configure(state='disabled')
    loading_label.pack(pady=(6, 0))
    clear_results()
    Thread(target=run_processing, args=(current_file,), daemon=True).start()


def open_image():
    if current_file and path.isfile(current_file):
        startfile(current_file)


if __name__ == '__main__':
    freeze_support()

    set_appearance_mode('dark')
    set_default_color_theme('blue')

    window = CTk()
    window.title('Algorítmo Físico')
    window.geometry('960x700')
    window.minsize(760, 520)
    window.state('zoomed')

    header_frame = CTkFrame(window, fg_color='transparent')
    header_frame.pack(fill='x', padx=16, pady=(16, 0))

    left_header = CTkFrame(header_frame, fg_color='transparent')
    left_header.pack(side='left', fill='both', expand=True)

    top = CTkFrame(left_header, fg_color='transparent')
    top.pack(fill='x')

    CTkButton(
        top, text='🖼  Selecionar Imagem',
        command=select_image,
        height=42, corner_radius=8,
        font=CTkFont(size=16, weight='bold')
    ).pack(side='left')

    CTkButton(
        top, text='📂  Selecionar Pasta',
        command=select_folder,
        height=42, corner_radius=8,
        font=CTkFont(size=16, weight='bold')
    ).pack(side='left', padx=(8, 0))

    path_label = CTkLabel(
        top, text='',
        font=CTkFont(size=15), text_color='gray60'
    )
    path_label.pack(side='left', padx=12)

    sel_row = CTkFrame(left_header, fg_color='transparent')
    sel_row.pack(fill='x', pady=(10, 0))

    CTkLabel(
        sel_row, text='Imagem:',
        font=CTkFont(size=16, weight='bold')
    ).pack(side='left')

    img_menu = CTkOptionMenu(
        sel_row, values=['—'],
        width=340, height=38, corner_radius=8,
        font=CTkFont(size=15),
        state='disabled',
        command=on_img_menu_change
    )
    img_menu.pack(side='left', padx=8)

    run_btn = CTkButton(
        sel_row, text='▶  Processar',
        command=process,
        height=38, corner_radius=8,
        font=CTkFont(size=15, weight='bold'),
        state='disabled'
    )
    run_btn.pack(side='left', padx=(4, 0))

    preview_btn = CTkButton(
        header_frame, text='Nenhuma\nimagem', image=None,
        command=open_image,
        width=160, height=160, corner_radius=8,
        font=CTkFont(size=14),
        fg_color='#222528', hover_color='#2c3034',
        state='disabled'
    )
    preview_btn.pack(side='right', padx=(16, 0))

    loading_label = CTkLabel(
        window, text='⏳ Processando...',
        font=CTkFont(size=16), text_color='#f1c40f'
    )

    results = CTkFrame(window, fg_color='transparent')
    results.pack(fill='both', expand=True, padx=16, pady=(12, 16))
    results.grid_columnconfigure(0, weight=1)
    results.grid_columnconfigure(1, weight=1)
    results.grid_rowconfigure(1, weight=0)
    results.grid_rowconfigure(3, weight=1)

    output_title = CTkLabel(
        results, text='Saída',
        font=CTkFont(size=16, weight='bold'),
        text_color='#bfbfbf'
    )
    output_title.grid(row=0, column=0, columnspan=2, sticky='w', pady=(0, 4))

    output_box = CTkTextbox(
        results, font=CTkFont(family='Consolas', size=20),
        fg_color='#222528', corner_radius=8,
        text_color='#0f0', state='disabled', wrap='none',
        height=LINE_HEIGHT
    )
    output_box.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0, 10))

    CTkLabel(
        results, text='Pseudocódigo',
        font=CTkFont(size=16, weight='bold'),
        text_color='#bfbfbf'
    ).grid(row=2, column=0, sticky='w', pady=(0, 4))

    CTkLabel(
        results, text='Python',
        font=CTkFont(size=16, weight='bold'),
        text_color='#bfbfbf'
    ).grid(row=2, column=1, sticky='w', pady=(0, 4))

    pseudo_box = CTkTextbox(
        results, font=CTkFont(family='Consolas', size=20),
        fg_color='#222528', corner_radius=8,
        text_color='#0f0', state='disabled', wrap='none'
    )
    pseudo_box.grid(row=3, column=0, sticky='nsew', padx=(0, 6))

    python_box = CTkTextbox(
        results, font=CTkFont(family='Consolas', size=20),
        fg_color='#222528', corner_radius=8,
        text_color='#0f0', state='disabled', wrap='none'
    )
    python_box.grid(row=3, column=1, sticky='nsew', padx=(6, 0))

    window.mainloop()