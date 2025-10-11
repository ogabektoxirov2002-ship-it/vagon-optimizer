import streamlit as st
from itertools import permutations

st.set_page_config(page_title="Оптимизация подачи вагонов", page_icon="🚂", layout="centered")

st.title("🚂 Оптимизация подачи вагонов несколькими маневровыми локомотивами")

st.write("Введите параметры станционных путей и фронтов:")

# === Ввод данных ===
num_paths = st.number_input("Количество соединительных путей:", min_value=1, step=1)

front_data = []
front_counter = 1
for path in range(1, num_paths + 1):
    n_fronts = st.number_input(f"Путь {path}: количество фронтов", min_value=1, step=1, key=f"fr{path}")
    for f in range(1, n_fronts + 1):
        n = st.number_input(f"  Фронт {front_counter}: количество вагонов", min_value=1, step=1, key=f"n{front_counter}")
        t = st.number_input(f"  Фронт {front_counter}: время от станции (часы)", min_value=0.0, step=0.1, key=f"t{front_counter}")
        front_data.append((n, t))
        front_counter += 1

num_loco = st.number_input("Количество маневровых локомотивов:", min_value=1, step=1)

# === Алгоритмы ===
def L_for_order(order, n, tau):
    L = 0
    for k in range(len(order)):
        cum = sum(tau[j] for j in order[k:])
        L += n[order[k]] * cum
    return L

def smith_order(indices, n, tau):
    return sorted(indices, key=lambda i: (tau[i] / n[i], i))

def find_optimal_order_for_set(indices, n, tau):
    if len(indices) <= 8:
        bestL = float("inf")
        best_order = None
        for perm in permutations(indices):
            curL = L_for_order(list(perm), n, tau)
            if curL < bestL:
                bestL = curL
                best_order = list(perm)
        return best_order, bestL
    else:
        ords = smith_order(indices, n, tau)
        return ords, L_for_order(ords, n, tau)

def divide_indices(indices, m):
    chunks = [[] for _ in range(m)]
    for i, idx in enumerate(indices):
        chunks[i % m].append(idx)
    return chunks

def format_groups(lst):
    return [i + 1 for i in lst]

# === Кнопка "Рассчитать" ===
if st.button("Рассчитать оптимальный вариант"):
    if len(front_data) == 0:
        st.warning("⚠️ Сначала введите хотя бы один фронт!")
    else:
        n = [g[0] for g in front_data]
        tau = [g[1] for g in front_data]
        t = len(n)

        st.subheader("📋 Введённые данные:")
        for i in range(t):
            st.write(f"Фронт {i+1}: n={n[i]}, τ={tau[i]}")

        # Один локомотив
        full_order, L_single = find_optimal_order_for_set(list(range(t)), n, tau)
        st.write(f"**Однолокомотивный вариант:** порядок {format_groups(full_order)}, L = {L_single:.3f}")

        if num_loco == 1:
            st.success(f"Все фронты обслуживает один локомотив, суммарные вагоно-часы: {L_single:.3f}")
        else:
            indices = smith_order(list(range(t)), n, tau)
            parts = divide_indices(indices, num_loco)

            total_L = 0
            st.subheader("🚜 Результаты по локомотивам:")
            for loco in range(num_loco):
                order, Lval = find_optimal_order_for_set(parts[loco], n, tau)
                total_L += Lval
                st.write(f"Локомотив {loco+1}: фронты {format_groups(order)}, L = {Lval:.3f}")

            st.success(f"**Суммарные вагоно-часы:** {total_L:.3f}")
            st.info(f"💰 Экономия по сравнению с одним локомотивом: {L_single - total_L:.3f}")
