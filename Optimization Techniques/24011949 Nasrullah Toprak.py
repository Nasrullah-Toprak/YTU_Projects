import os
import csv
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from sentence_transformers import SentenceTransformer
import time
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
import re


# Eğitim ve Test Kümesini TXT Dosyalarından Oluşturma 
folder = os.path.dirname(os.path.abspath(__file__))
egitim_csv_path = os.path.join(folder, "Eğitim Kümesi.csv")
test_csv_path = os.path.join(folder, "Test Kümesi.csv")

def read_files_to_dataset(prefix="Eğitim Kümesi"):
    file_list = [f for f in os.listdir(folder) if f.startswith(prefix) and f.endswith(".txt")]
    
    def extract_index(filename):
        match = re.search(r'Soru (\d+)\.txt', filename)
        return int(match.group(1)) if match else -1

    file_list.sort(key=extract_index)
    
    dataset_list = []
    
    if not file_list:
        print(f"Hata: '{prefix}' ön ekiyle başlayan TXT dosyası bulunamadı. Lütfen önce mevcut kodu çalıştırın.")
        return []

    for i in range(0, len(file_list), 2):
        
        match_good = re.search(r'Soru (\d+)\.txt', file_list[i])
        match_bad = re.search(r'Soru (\d+)\.txt', file_list[i+1])

        if not match_good or not match_bad:
            print(f"Hata: Dosya isimleri formatı bozuk. {file_list[i]}, {file_list[i+1]}")
            continue

        index_good = int(match_good.group(1))
        index_bad = int(match_bad.group(1))

        if index_bad != index_good + 1:
            print(f"Hata: {index_good} ve {index_bad} numaralı sorular aynı soruya ait değil veya sırası bozuk.")
            continue

        file_path_good = os.path.join(folder, file_list[i]) # 1. İyi Cevap Dosyasını Oku (+1)
        with open(file_path_good, "r", encoding="utf-8") as f:
            lines_good = f.readlines()
            
        file_path_bad = os.path.join(folder, file_list[i+1]) # 2. Kötü Cevap Dosyasını Oku (-1)
        with open(file_path_bad, "r", encoding="utf-8") as f:
            lines_bad = f.readlines()

        soru_cevap_iyi = lines_good[0].strip().split(" | ")
        soru_iyi = soru_cevap_iyi[0].strip()
        cevap_iyi = soru_cevap_iyi[1].strip()
        label_iyi = int(lines_good[1].strip())

        soru_cevap_kotu = lines_bad[0].strip().split(" | ")
        soru_kotu = soru_cevap_kotu[0].strip()
        cevap_kotu = soru_cevap_kotu[1].strip()
        label_kotu = int(lines_bad[1].strip())
        
        if soru_iyi != soru_kotu:
             print(f"Uyarı: İki ardışık dosyada farklı sorular var. {soru_iyi} vs {soru_kotu}")
             
        if label_iyi != 1 or label_kotu != -1:
             print(f"Uyarı: Etiketler +1/-1 beklentisiyle uyuşmuyor. {label_iyi} vs {label_kotu}")

        dataset_list.append({
            "soru": soru_iyi, 
            1: cevap_iyi, 
            -1: cevap_kotu
        })
        
    print(f"'{prefix}' için {len(dataset_list)} soru başarıyla yüklendi.")
    return dataset_list

egitim_kumesi = read_files_to_dataset("Eğitim Kümesi")
test_kumesi = read_files_to_dataset("Test Kümesi")

egitim_dataset = []
test_dataset = []

def create_dataset_from_list(data_list, dataset_list):
    for soru_dict in data_list:
        soru = soru_dict["soru"]
        cevap_iyi = soru_dict[1]
        cevap_kotu = soru_dict[-1]
        
        dataset_list.append([soru, cevap_iyi, 1])
        dataset_list.append([soru, cevap_kotu, -1])

        """
        egitim_dataset[
            {"soru": "", 1:"", -1:""}
        ]
        """

create_dataset_from_list(egitim_kumesi, egitim_dataset)
create_dataset_from_list(test_kumesi, test_dataset)




# Dataset CSV kaydet (Korundu, ancak artık listelerden yazılıyor)
# Eğitim CSV
with open(egitim_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["soru", "cevap", "label"])
    writer.writerows(egitim_dataset)
print(f"Eğitim Kümesi.csv başarıyla oluşturuldu! (Toplam {len(egitim_dataset)} kayıt)")

# Test CSV
with open(test_csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["soru", "cevap", "label"])
    writer.writerows(test_dataset)
print(f"Test Kümesi.csv başarıyla oluşturuldu! (Toplam {len(test_dataset)} kayıt)")
all_dataset = egitim_dataset + test_dataset # Tüm veri setini birleştir




# Soru ve Cevap Embeddinglerini Ayrı Ayrı Oluşturma
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SentenceTransformer('ytu-ce-cosmos/turkish-e5-large').to(device)

def get_detailed_instruct(task_description: str, query: str) -> str: # E5 model ailesi için instruct formatı korundu
    return f'Instruct: {task_description}\nQuery: {query}'

task_soru = 'Represent the Turkish query for retrieval'
task_cevap = 'Represent the Turkish document for retrieval'

# Veri kümelerini ayırma
soru_texts = [soru for soru, _, _ in all_dataset]
cevap_texts = [cevap for _, cevap, _ in all_dataset]
labels = torch.tensor([label for _, _, label in all_dataset], dtype=torch.float32)

# Soru ve Cevap Girişleri
input_texts_soru = [get_detailed_instruct(task_soru, q) for q in soru_texts]
input_texts_cevap = [get_detailed_instruct(task_cevap, a) for a in cevap_texts]
print("Soru ve Cevap Embeddingleri ayrı ayrı oluşturuluyor, bekleyin...")

# Soru ve Cevap Embeddingleri
embeddings_soru = model.encode(input_texts_soru, convert_to_tensor=True, normalize_embeddings=True)
embeddings_cevap = model.encode(input_texts_cevap, convert_to_tensor=True, normalize_embeddings=True)
print(f"Soru Embedding boyutu: {embeddings_soru.shape}")
print(f"Cevap Embedding boyutu: {embeddings_cevap.shape}")
print("Embeddingler başarıyla oluşturuldu.")

# Embeddingleri kaydet (.pt ve .npy)
emb_soru_pt_path = os.path.join(folder, "embeddings_soru.pt")
emb_cevap_pt_path = os.path.join(folder, "embeddings_cevap.pt")
labels_path = os.path.join(folder, "labels.npy")
torch.save(embeddings_soru, emb_soru_pt_path)
torch.save(embeddings_cevap, emb_cevap_pt_path)
np.save(labels_path, labels.numpy())
print("Embeddingler ve label'lar kaydedildi:")
print(f"Soru PyTorch: {emb_soru_pt_path}")
print(f"Cevap PyTorch: {emb_cevap_pt_path}")
print(f"Label: {labels_path}")





# Model Eğitimi ve Karşılaştırma Kriterleri
D = embeddings_soru.shape[1]
INPUT_SIZE = 2*D + 1 # Concat(Soru, Cevap)

# Veri kümelerini ayırma
egitim_emb_soru = embeddings_soru[:len(egitim_dataset)]
egitim_emb_cevap = embeddings_cevap[:len(egitim_dataset)]
egitim_labels = labels[:len(egitim_dataset)].unsqueeze(1)
test_emb_soru = embeddings_soru[len(egitim_dataset):]
test_emb_cevap = embeddings_cevap[len(egitim_dataset):]
test_labels = labels[len(egitim_dataset):].unsqueeze(1)

# Veri Yükleyicileri
BATCH_SIZE = 1
train_dataset = TensorDataset(egitim_emb_soru, egitim_emb_cevap, egitim_labels)
test_dataset = TensorDataset(test_emb_soru, test_emb_cevap, test_labels)
train_loader_sgd = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
train_loader_gd = DataLoader(train_dataset, batch_size=len(egitim_dataset), shuffle=False) # GD için tam batch
test_loader = DataLoader(test_dataset, batch_size=len(test_dataset), shuffle=False)

class SimpleClassifier(nn.Module):
    def __init__(self, input_size):
        super(SimpleClassifier, self).__init__()
        # W matrisi (1, 2d+1) boyutunda
        self.W = nn.Linear(input_size, 1, bias=False)
        self.activation = nn.Tanh()

    def forward(self, x_q, x_a):
        # x_q ve x_a'yı birleştir: (Batch_size, 2D)
        x_concat = torch.cat((x_q, x_a), dim=1)
        # Girişe Bias terimi için 1 eklendi: (Batch_size, 2D+1)
        bias_term = torch.ones(x_concat.size(0), 1, device=device)
        x_with_bias = torch.cat((bias_term, x_concat), dim=1)
        # Çıktı: tanh(W*x)
        output = self.W(x_with_bias)
        return self.activation(output)

# Performans Fonksiyonu
def evaluate(model, data_loader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x_q, x_a, labels in data_loader:
            x_q, x_a, labels = x_q.to(device), x_a.to(device), labels.to(device)
            outputs = model(x_q, x_a)
            predicted = torch.sign(outputs)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
    return correct / total

# Eğitim Fonksiyonu
def train_model(initial_weights, optimizer_type, batch_size, lr, epochs=200):
    model_local = SimpleClassifier(INPUT_SIZE).to(device) # Modeli Başlat

    # Başlangıç ağırlıklarını ayarla
    with torch.no_grad():
        model_local.W.weight.copy_(initial_weights.T) #(1, INPUT_SIZE)

    if optimizer_type == 'GD':
        optimizer = optim.SGD(model_local.parameters(), lr=lr)
        train_loader = train_loader_gd
    elif optimizer_type == 'SGD':
        optimizer = optim.SGD(model_local.parameters(), lr=lr)
        train_loader = train_loader_sgd
    elif optimizer_type == 'Adam':
        optimizer = optim.Adam(model_local.parameters(), lr=lr)
        train_loader = train_loader_sgd
    else:
        raise ValueError("Geçersiz Optimizasyon Tipi")

    criterion = nn.MSELoss()

    history = {'time': [], 'updates': [], 'train_acc': [], 'test_acc': [], 'train_loss': []}
    
    # Yeni: Ağırlık yörüngesi kaydı
    weight_trajectory = [] 

    start_time = time.time()
    update_count = 0
    
    # Yeni: İlk ağırlığı kaydet
    weight_trajectory.append(model_local.W.weight.data.cpu().numpy().flatten())

    for epoch in range(epochs):
        model_local.train()
        total_loss = 0

        for x_q, x_a, labels in train_loader:
            x_q, x_a, labels = x_q.to(device), x_a.to(device), labels.to(device)

            optimizer.zero_grad()
            outputs = model_local(x_q, x_a)

            loss = criterion(outputs, labels)
            loss.backward()

            optimizer.step()
            update_count += 1
            total_loss += loss.item() * x_q.size(0)

            # Her güncellemede (GD'de her epoch'ta) kaydı almak   
            is_gd_step = (optimizer_type == 'GD' and update_count % 1 == 0)
            is_sgd_adam_step = (optimizer_type != 'GD' and update_count % 100 == 0)

            if is_gd_step or is_sgd_adam_step: # or (epoch == epochs - 1 and update_count == len(egitim_dataset)):
                train_acc = evaluate(model_local, train_loader_gd)
                test_acc = evaluate(model_local, test_loader)
                
                # Yeni: Ağırlığı kaydet (CPU'ya çek, Numpy'a çevir, düzleştir)
                weight_trajectory.append(model_local.W.weight.data.cpu().numpy().flatten())
                history['time'].append(time.time() - start_time)
                history['updates'].append(update_count)
                history['train_acc'].append(train_acc)
                history['test_acc'].append(test_acc)
                history['train_loss'].append(total_loss / len(egitim_dataset) if optimizer_type != 'GD' else loss.item())
        
        # Epoch sonunda GD için kayıp/başarıyı güncelle (SGD/Adam için zaten güncelleme yapıldı)
        if optimizer_type == 'GD' and epoch < epochs-1 and (update_count % 100 != 0): # Son epoch'ta zaten kaydedilmişse atla
             train_acc = evaluate(model_local, train_loader_gd)
             test_acc = evaluate(model_local, test_loader)
             total_loss = loss.item() # GD'de loss zaten tam batch loss

             weight_trajectory.append(model_local.W.weight.data.cpu().numpy().flatten())
             history['time'].append(time.time() - start_time)
             history['updates'].append(update_count)
             history['train_acc'].append(train_acc)
             history['test_acc'].append(test_acc)
             history['train_loss'].append(total_loss)

    return history, model_local, np.array(weight_trajectory)

# Karşılaştırma Döngüsü Hiperparametreler
NUM_TRIALS = 5
EPOCHS = 200
LEARNING_RATE = 0.01
seeds = np.random.randint(0, 10000, NUM_TRIALS)
results = {}
weight_trajectories = {opt_type: [] for opt_type in ['GD', 'SGD', 'Adam']} # Yeni: Ağırlık yörüngelerini kaydetmek için
print("\n\nOptimizasyon Algoritmaları Karşılaştırması Başlatılıyor")

for i in range(NUM_TRIALS):
    np.random.seed(seeds[i])
    torch.manual_seed(seeds[i])

    # Başlangıç Ağırlıklarını Rastgele Oluştur (W: (INPUT_SIZE)x1)
    initial_weights = torch.randn(INPUT_SIZE, 1, device=device) * 0.01

    print(f"\n--- Deneme {i+1} / {NUM_TRIALS} (Seed: {seeds[i]}) ---")

    for opt_type in ['GD', 'SGD', 'Adam']:
        print(f"Eğitim: {opt_type}")

        # GD için daha büyük LR
        lr = LEARNING_RATE * 10 if opt_type == 'GD' else LEARNING_RATE
        history, _, trajectory = train_model(initial_weights.clone(), opt_type, BATCH_SIZE, lr, epochs=EPOCHS)

        if (opt_type, i) not in results:
            results[(opt_type, i)] = history
            
        # Yeni: Yörüngeyi kaydet
        weight_trajectories[opt_type].append(trajectory)
        print(f"{opt_type} - Son Eğitim Başarısı: {history['train_acc'][-1]:.4f}, Son Test Başarısı: {history['test_acc'][-1]:.4f}")




# Sonuçların Grafiği
def plot_results(results, metric, x_axis, title_suffix, num_trials):
    plt.figure(figsize=(12, 6))
    for opt_type in ['GD', 'SGD', 'Adam']:
        history_first = results.get((opt_type, 0))
        if history_first:
            plt.plot(history_first[x_axis], history_first[metric], label=f'{opt_type} (Deneme 1)', alpha=0.8)

    x_label = x_axis.capitalize().replace('updates', 'Güncelleme Sayısı').replace('time', 'Süre (s)')
    y_label = metric.replace('_', ' ').capitalize().replace('acc', 'Başarısı').replace('loss', 'Kaybı')

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(f'Optimizasyon Algoritmaları Karşılaştırması - {title_suffix}')
    plt.legend()
    plt.grid(True)
    plt.show()

print("\n\n\nGrafiklerin Oluşturulması")
plot_results(results, 'train_acc', 'time', 'Eğitim Başarısı vs Süre', NUM_TRIALS)
plot_results(results, 'test_acc', 'time', 'Test Başarısı vs Süre', NUM_TRIALS)
plot_results(results, 'train_loss', 'time', 'Eğitim Kaybı vs Süre', NUM_TRIALS)
plot_results(results, 'train_acc', 'updates', 'Eğitim Başarısı vs Güncelleme Sayısı', NUM_TRIALS)
plot_results(results, 'test_acc', 'updates', 'Test Başarısı vs Güncelleme Sayısı', NUM_TRIALS)
plot_results(results, 'train_loss', 'updates', 'Eğitim Kaybı vs Güncelleme Sayısı', NUM_TRIALS)




# b KISMI - W(t) 2 Boyutta  Görselleştirme
def plot_tye_w(weight_trajectories, opt_type, n_components=2, perplexity=30): 
    trajectories = weight_trajectories[opt_type]
    if not trajectories:
        print(f"Hata: {opt_type} için kaydedilmiş yörünge yok.")
        return

    all_weights = np.concatenate(trajectories, axis=0) # Tüm ağırlık vektörlerini tek bir matriste birleştir
    print(f"\n{opt_type} Ağırlık Yörüngeleri için T-SNE uygulanıyor ({all_weights.shape[0]} vektör)...") # T-SNE Uygulama
    tsne = TSNE(   # n_iter_early_exag: GD için düşük güncelleme sayısı nedeniyle artırıldı
        n_components=n_components,
        perplexity=perplexity,
        random_state=42
    )
  
    try:
        tsne_results = tsne.fit_transform(all_weights)
    except Exception as e:
        print(f"T-SNE Uygulama Hatası: {e}")
        return

    # T'YE sonuçlarını denemelere ayır
    start_index = 0
    tsne_trajectories = []
    for traj in trajectories:
        end_index = start_index + traj.shape[0]
        tsne_trajectories.append(tsne_results[start_index:end_index])
        start_index = end_index

    # Grafiği Çizme
    plt.figure(figsize=(10, 8))
    colors = plt.cm.viridis(np.linspace(0, 1, NUM_TRIALS))
    
    for i, tsne_traj in enumerate(tsne_trajectories):
        plt.plot(tsne_traj[:, 0], tsne_traj[:, 1], color=colors[i], 
                 label=f'Deneme {i+1} (Seed: {seeds[i]})', alpha=0.7)
        
        # Başlangıç ve Bitiş Noktalarını İşaretle
        plt.scatter(tsne_traj[0, 0], tsne_traj[0, 1], color=colors[i], marker='o', s=100, label=f'Başlangıç {i+1}' if i == 0 else None)
        plt.scatter(tsne_traj[-1, 0], tsne_traj[-1, 1], color=colors[i], marker='*', s=200, label=f'Bitiş {i+1}' if i == 0 else None)

    plt.title(f'{opt_type} Optimizasyon Ağırlık Yörüngesi (t-SNE İndirgenmiş)')
    plt.xlabel('t-SNE Boyut 1')
    plt.ylabel('t-SNE Boyut 2')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.show()

print(" \n\nAğırlık Yörüngesi (W(t)) Görselleştirmesi (T-SNE)")
plot_tye_w(weight_trajectories, 'GD')
plot_tye_w(weight_trajectories, 'SGD')
plot_tye_w(weight_trajectories, 'Adam')