#Proje Konusu Bu proje asgari ücret ile aylık evde yemek yapma maliyeti arasında bir karşılaştırma projesidir.

#Kullanılan Kütüphaneler pandas, json, sklearn, os, sys, subprocess, Image, ImageTK, shutil, tkinter, seaborn, matplotlib.pyplot, re, urllib.parse, requests, bs4, time, random, openpyxl

#Proje Adımları İlgili yemek tarifi verileri ye-mek.net, fiyat verileri www.cimri.com adresinden alınmıştır. Ön işleme adımları ile birimler standartlaştırılmıştır (adet, kg, bir tutam tuz vs). TF-IDF ve Kosinüs Benzerliği kullanılarak ilgili yemek tarifi malzemeleri ile fiyatlar eşleştirilmiştir. Eşleşen fiyatlar birim bazındadır. Malzeme miktarı ile çarpılarak fiyat hesaplaması yapılmıştır. Günlük 3 öğün (kahvaltı, öğle yemeği, akşam yemeği) ve 30 gün için yemek planı oluşturulmuştur.

Sonuçlar Ortalama günlük maliyet: 348,85 ₺ Aylık toplam maliyet: 10.453,54 ₺ Asgari ücretin yaklaşık %47,3'ü (2025 Ocak itibarıyla net asgari ücret = 22.104 ₺)

Yemek maliyetlerinin yanında kira, faturalar, sağlık gibi kalemler de düşünüldüğünde asgari ücretle geçim önemli bir tartışma konusu olmaktadır.
