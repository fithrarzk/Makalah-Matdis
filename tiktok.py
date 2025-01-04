import networkx as nx
import random

class TikTokFYP:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.videos = [
            "Video Kucing Lucu",
            "Valorant Clip",
            "Dance Tiktok Trend Baru",
            "Jedag Jedug",
            "Seputar Saham",
            "Seputar Materi Kuliah",
            "Meme Viral",
            "Berita",
            "Clip Film",
            "Lirik Lagu"
        ]
        self.users = []

    def add_user(self, user_id):
        if user_id not in self.graph:
            self.graph.add_node(user_id, type="user")
            self.users.append(user_id)

    def add_video(self):
        for video in self.videos:
            if video not in self.graph:
                self.graph.add_node(video, type="video")

    def interact_with_video(self, user_id, video_id, like=0, comment=0, share=0, bookmark=0, full_watch=0):
        if video_id in self.videos:
            weight = (like * 1.5 + comment * 2.0 + share * 3.0 + bookmark * 2.5 + full_watch * 1.25)
            if self.graph.has_edge(user_id, video_id):
                self.graph[user_id][video_id]['weight'] += weight
            else:
                self.graph.add_edge(user_id, video_id, weight=weight)
        else:
            print("Video tidak ditemukan.")

    def recommend_videos_for_user(self, user_id, top_k=5):
        if user_id not in self.graph:
            return []

        # Hitung PageRank
        pagerank_scores = nx.pagerank(self.graph, weight='weight')
        recommendations = sorted(
            (
                (node, score) for node, score in pagerank_scores.items()
                if self.graph.nodes[node]['type'] == 'video'
            ),
            key=lambda x: x[1],
            reverse=True
        )
        return recommendations[:top_k]


def main():
    fyp = TikTokFYP()

    # Tambahkan pengguna
    user_id = "user_1"
    fyp.add_user(user_id)

    # Tambahkan video
    fyp.add_video()

    while True:
        print("\nMenu:")
        print("1. Lihat Video Berikutnya")
        print("2. Lihat Kemungkinan FYP")
        print("3. Keluar")
        
        choice = input("Pilih opsi (1/2/3): ")

        if choice == "1":
            recommendations = fyp.recommend_videos_for_user(user_id, top_k=len(fyp.videos))
            
            if recommendations:
                # Ambil video secara acak dengan bobot probabilitas dari skor
                videos, scores = zip(*recommendations)
                video_choice = random.choices(videos, weights=scores, k=1)[0]
            else:
                # Jika tidak ada rekomendasi, pilih secara acak
                video_choice = random.choice(fyp.videos)
                
            print(f"\nAnda sedang menonton video: {video_choice}")

            watch_full = input("Apakah anda menonton full? (Full/Sebagian/Skip): ").strip().lower()     

            if watch_full == "full" or watch_full == "sebagian":
                if watch_full == "full":
                    full_watch = 1
                elif watch_full == "sebagian":
                    full_watch = 0.5

                print("\nApakah anda akan:")
                like = int(input("Like video ini? (1 untuk Ya, 0 untuk Tidak): "))
                comment = int(input("Comment video ini? (1 untuk Ya, 0 untuk Tidak): "))
                share = int(input("Share video ini? (1 untuk Ya, 0 untuk Tidak): "))
                bookmark = int(input("Bookmark video ini? (1 untuk Ya, 0 untuk Tidak): "))
                fyp.interact_with_video(user_id, video_choice, like=like, comment=comment, share=share, bookmark=bookmark, full_watch=full_watch)
            else:
                full_watch = 0

            print(f"Interaksi dengan video {video_choice} tercatat!")

        elif choice == "2":
            print("\nDaftar Kemungkinan FYP:")
            recommendations = fyp.recommend_videos_for_user(user_id)
            for video, score in recommendations:
                print(f"{video}, Score: {score:.4f}")

        elif choice == "3":
            print("Keluar dari program. Terima kasih!")
            break

        else:
            print("Pilihan tidak valid. Coba lagi.")

if __name__ == "__main__":
    main()
