import os 
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import shutil

window = Tk()
window.iconbitmap(r'D:\Perso\ProjetCode\CompareFile\logo.ico')



# Créer le style
style = ttk.Style(window)
style.theme_use("default")

def switch_frame1():
    frame.pack_forget()
    main_frame.pack(expand=True)
    
def show_results():
    window.geometry("1450x360")
    main_frame.pack_forget()
    results_frame.pack(expand=True)
    
def return_to_main():
    results_frame.pack_forget() 
    window.geometry("480x360")
    entry1.delete(0, END)
    entry2.delete(0, END)
    results_table.delete(*results_table.get_children())
    main_frame.pack(expand=True)
    
    
def select_directory(entry):
    directory = filedialog.askdirectory()
    directory = directory.replace('/', '\\')  # Ajoutez cette ligne pour normaliser le chemin
    entry.delete(0, END)  # Efface le contenu actuel de la boîte de texte
    entry.insert(0, directory)  # Insère le nouveau chemin

def compare_directories():
    source = entry1.get()
    target = entry2.get()
    
    results_table.heading('chemin_source', text=f'Chemin Dir1 : {source}')
    results_table.heading('chemin_cible', text=f'Chemin Dir2 : {target}')
    
    if not os.path.exists(source):
        messagebox.showwarning("Erreur ! ","L'un des répertoires n'existe pas.")
        entry1.delete(0, END)
        return
    elif not os.path.exists(target):
        messagebox.showwarning("Erreur ! ","L'un des répertoires n'existe pas.")
        entry2.delete(0, END)
        return
    
    # Nettoyage du Treeview avant de remplir avec de nouvelles données
    results_table.delete(*results_table.get_children())

    # Comparaison des fichiers dans les répertoires
    compare_files(source, target)
    
def compare_files(dir1, dir2):
    # Dictionnaires pour stocker les chemins complets et les tailles des fichiers
    files_dir1 = {}
    files_dir2 = {}

    # Fonction récursive pour parcourir les dossiers et sous-dossiers
    def get_files_recursive(directory, files_dict, base_path=""):
        for entry in os.scandir(directory):
            if entry.is_file():
                # Ajoutez le chemin de base au chemin relatif de l'entrée
                relative_path = os.path.join(base_path, entry.name)
                files_dict[relative_path] = os.path.getsize(entry.path)
            elif entry.is_dir():
                # Mettez à jour le chemin de base pour inclure le dossier actuel
                new_base = os.path.join(base_path, entry.name)
                get_files_recursive(entry.path, files_dict, new_base)


    get_files_recursive(dir1, files_dir1)
    get_files_recursive(dir2, files_dir2)

    # Comparaison des noms de fichiers
    unique_to_dir1 = set(files_dir1.keys()) - set(files_dir2.keys())
    unique_to_dir2 = set(files_dir2.keys()) - set(files_dir1.keys())
    common_files = set(files_dir1.keys()).intersection(files_dir2.keys())

    # Ajout des résultats au Treeview
    for file in unique_to_dir1:
        clean_path = file.lstrip("/\\")  # Chemin relatif sans les caractères de début
        results_table.insert('', 'end', values=(clean_path, files_dir1[file], 'Copier vers dir2', '', ''), tags=('bordered',))
    for file in unique_to_dir2:
        clean_path = file.lstrip("/\\")
        results_table.insert('', 'end', values=('', '', 'Copier vers dir1', clean_path, files_dir2[file]), tags=('bordered',))
        
    # Ajout des résultats au Treeview pour les fichiers communs avec des tailles différentes
    for file in common_files:
        size_dir1 = files_dir1[file]
        size_dir2 = files_dir2[file]
        if size_dir1 != size_dir2:
            results_table.insert('', 'end', values=(file, size_dir1, 'Résoudre différence', file, size_dir2))
    show_results()


# Fonction pour copier un fichier d'un répertoire source à un répertoire cible
def copy_file(source_dir, target_dir, relative_path):
    # Assurez-vous d'utiliser des chemins relatifs pour la copie
    relative_path = relative_path.strip("/\\")  # Enlève les slashs de début et de fin
    
    # Construisez le chemin complet vers le fichier source et cible
    source_file = os.path.join(source_dir, relative_path)
    target_file = os.path.join(target_dir, relative_path)

    # Assurez-vous que le répertoire cible existe
    target_dir_path = os.path.dirname(target_file)
    os.makedirs(target_dir_path, exist_ok=True)

    try:
        # Copiez le fichier
        shutil.copy(source_file, target_file)
        messagebox.showinfo("Copie réussie", f"Fichier copié de {source_file} à {target_file}")
        return True
    except IOError as e:
        messagebox.showerror("Erreur de copie", f"Impossible de copier le fichier. {e}")
        return False


# Ajout d'un gestionnaire pour les clics sur l'arborescence
def on_treeview_click(event):
    if not results_table.identify_region(event.x, event.y) == "cell":
        return

    row_id = results_table.identify_row(event.y)
    column = results_table.identify_column(event.x)
    
    # Vérifiez si la colonne d'action a été cliquée
    if column == '#3':
        item = results_table.item(row_id)
        values = item['values']
        # Déterminez la direction de la copie en fonction de l'action affichée
        if values[2] == 'Copier vers dir2':
            success = copy_file(entry1.get(), entry2.get(), values[0])
        elif values[2] == 'Copier vers dir1':
            success = copy_file(entry2.get(), entry1.get(), values[3])
        if values[2] == 'Résoudre différence':
            # Demandez à l'utilisateur quel fichier conserver
            response = messagebox.askyesnocancel("Résoudre la différence de taille", 
                                                 "Choisissez le fichier à conserver:\n"
                                                 "Oui pour conserver celui de dir1: {} (taille: {})\n"
                                                 "Non pour conserver celui de dir2: {} (taille: {})\n"
                                                 .format(os.path.join(entry1.get(), values[0]), values[1], os.path.join(entry2.get(), values[3]), values[4]),
                                                 icon='warning')
            if response is True:  # Si l'utilisateur choisit de garder le fichier de dir1
                success = copy_file(entry2.get(), entry1.get(), values[0])
            elif response is False:  # Si l'utilisateur choisit de garder le fichier de dir2
                success = copy_file(entry1.get(), entry2.get(), values[3])
            else:  # Si l'utilisateur annule l'action
                success = False
    
    if success:
        # Supprimez la ligne du Treeview
        results_table.delete(row_id)

def dir1():
    dir1 = entry1.get()
    return dir1

def dir2():
    dir2 = entry2.get()
    return dir2

#Personnalisation de la fenetre 
window.title("CompareFiles")
window.geometry("480x360")
window.minsize(480,360)
window.config(background='#41B77F')

#creation de la 1ere frame
frame = Frame(window, bg='#41B77F')

#texte de bienvenue
label_title = Label(frame, text="CompareFiles", font=("Courrier",40), bg='#41B77F', fg='white')
label_title.pack()
label_subtitle = Label(frame, text="Comparez et synchronisez vos fichiers", font=("Courrier",15), bg='#41B77F', fg='white')
label_subtitle.pack()

#creation d'un bouton
V_page_accueil = Button(frame, text="Page d'accueil", font=("Courrier",25), bg='white', fg='#41B77F', command=switch_frame1)
V_page_accueil.pack(pady=25, fill=X)

#ajouter frame
frame.pack(expand=True)

#creation de la frame principale
main_frame = Frame(window, bg='#41B77F')

#Bouton pour comparer les répertoires
button_compare = Button(main_frame, text="Comparer", font=("Courrier", 15), bg='white', fg='#41B77F', command=lambda: [compare_directories()])
button_compare.pack(pady=10)

# Boîte de texte et bouton pour le répertoire 1
label_source = Label(main_frame, text="Répertoire 1 :", bg='#41B77F', fg='white')
label_source.pack(pady=10)

entry1 = Entry(main_frame, width=50)
entry1.pack(pady=5)

button_source = Button(main_frame, text="Parcourir", command=lambda: select_directory(entry1))
button_source.pack(pady=5)

# Boîte de texte et bouton pour le répertoire 2
label_target = Label(main_frame, text="Répertoire 2 :", bg='#41B77F', fg='white')
label_target.pack(pady=10)

entry2 = Entry(main_frame, width=50)
entry2.pack(pady=5)

button_target = Button(main_frame, text="Parcourir", command=lambda: select_directory(entry2))
button_target.pack(pady=5)

# Frame pour afficher les résultats
results_frame = Frame(window, bg='#41B77F')

button_return = Button(results_frame, text="Retour", font=("Courrier", 15), bg='white', fg='#41B77F', command=return_to_main)
button_return.pack(side=LEFT, padx=10, pady=10)




# Création du Treeview
columns = ('chemin_source', 'taille_source', 'action', 'chemin_cible', 'taille_cible')
results_table = ttk.Treeview(results_frame, columns=columns, show='headings')


results_table.column('chemin_source', width=400)
results_table.heading('taille_source', text="Taille")
results_table.column('taille_source', width=150, anchor=CENTER)
    
results_table.heading('action', text="Action")
results_table.column('action', width=200, anchor=CENTER)
    

results_table.column('chemin_cible', width=400)
results_table.heading('taille_cible', text="Taille")
results_table.column('taille_cible', width=150, anchor=CENTER)
results_table.pack(expand=True)

results_table.bind('<ButtonRelease-1>', on_treeview_click)

# Empaqueter et cacher la frame des résultats
results_frame.pack(expand=True)
results_frame.pack_forget()

#afficher fenetre
window.mainloop()