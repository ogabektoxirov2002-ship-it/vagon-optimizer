import streamlit as st
from itertools import permutations

st.set_page_config(page_title="Оптимизация подачи вагонов", page_icon="🚂", layout="centered")

st.title("🚂 Оптимизация подачи вагонов на погрузочно-разгрузочные места несколькими маневровыми локомотивами")

st.write("Введите параметры станционных путей и фронтов:")

# === Ввод данных ===
num_paths = st.number_input("Количество соединительных путей:", min_value=1, step=1)

front_data = []
front_counter = 1
for path in range(1, num_paths + 1):
    n_fronts = st.number_input(f"Путь {path}: количество фронтов", min_value=1, step=1, key=f"fr{path}")
    for f in range(1, n_fronts + 1):
        n = st.number_input(f"  Фронт {front_counter}: количество вагонов", min_value=1, step=1, key=f"n{front_counter}")
        t = st.number_input(f"  Фронт {front_counter}: время от станции до фронта (часы)", min_value=0.0, step=0.1, key=f"t{front_counter}")
        front_data.append((n, t))
        front_counter += 1

num_loco = st.number_input("Количество маневровых локомотивов:", min_value=1, step=1)

# === Алгоритмы ===
def B_for_order(order, n, tau):
    B = 0
    for k in range(len(order)):
        cum = sum(tau[j] for j in order[k:])
        B += n[order[k]] * cum
    return B

def smith_order(indices, n, tau):
    return sorted(indices, key=lambda i: (tau[i] / n[i], i))

def find_optimal_order_for_set(indices, n, tau):
    bestB = float("inf")
    best_order = None
    for perm in permutations(indices):
        curB = B_for_order(list(perm), n, tau)
        if curB < bestB:
            bestB = curB
            best_order = list(perm)
    return best_order, bestB
    else:
        ords = smith_order(indices, n, tau)
        return ords, B_for_order(ords, n, tau)

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
        full_order, B_single = find_optimal_order_for_set(list(range(t)), n, tau)
        st.write(f"**Однолокомотивный вариант:** порядок {format_groups(full_order)}, B = {B_single:.3f}")

        if num_loco == 1:
            st.success(f"Все фронты обслуживает один локомотив, суммарные вагоно-часы: {B_single:.3f}")
        else:
            indices = smith_order(list(range(t)), n, tau)
            parts = divide_indices(indices, num_loco)

            total_B = 0
            st.subheader("🚂 Результаты по локомотивам:")
            for loco in range(num_loco):
                order, Bval = find_optimal_order_for_set(parts[loco], n, tau)
                total_B += Bval
                st.write(f"Локомотив {loco+1}: фронты {format_groups(order)}, B = {Bval:.3f}")

            st.success(f"**Суммарные вагоно-часы (B):** {total_B:.3f}")
            st.info(f"💰 Экономия по сравнению с одним локомотивом: {B_single - total_B:.3f}")



