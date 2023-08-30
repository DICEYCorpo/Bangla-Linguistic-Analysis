import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "serif"
plt.rcParams["text.usetex"] = True

# Sample data
labels = ['ধান', 'গম', 'বাজরা', 'মুগ', 'চিনাবাদাম']
values = [30, 20, 15, 10, 25]

plt.bar(labels, values)
plt.title(r'ফসল উৎপাদন')
plt.xlabel(r'ফসল')
plt.ylabel(r'উৎপাদন (মেট্রিক টন)')
plt.show()