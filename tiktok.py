import networkx as nx
import pandas as pd
import random
import matplotlib.pyplot as plt

class TikTokFYP:
    def __init__(self, dataset_path):
        self.graph = nx.DiGraph()
        self.videos = []
        self.users = []
        self.genre_scores = {}
        self.video_data = pd.read_csv(dataset_path)
        self.calculate_initial()

    def calculate_initial(self):
        for _, row in self.video_data.iterrows():
            video_id = row['id']
            genre = row['genre']
            if video_id not in self.graph:
                video_attributes = row.to_dict()
                video_attributes.pop('genre', None)
                initial_score = (
                    row['viewers'] * 0.125 +
                    row['likes'] * 0.5 +
                    row['comments'] * 0.25 +
                    row['shares'] * 0.5 +
                    row['saves'] * 0.25
                )
                self.graph.add_node(video_id, type="video", genre=genre, initial_score=initial_score, **video_attributes)
                self.videos.append(video_id)

                # Add initial score to genre_scores
                if genre not in self.genre_scores:
                    self.genre_scores[genre] = 0
                self.genre_scores[genre] += initial_score

    def add_user(self, user_id):
        if user_id not in self.graph:
            self.graph.add_node(user_id, type="user", genre_preferences={})
            self.users.append(user_id)

    def interact_with_video(self, user_id, video_id, like=0, comment=0, share=0, saves=0, full_watch=0):
        if video_id in self.videos:
            # Hitung bobot untuk interaksi
            weight = (like * 1.5 + comment * 1 + share * 1.25 + saves * 1.5 + full_watch * 1.0)
            genre = self.graph.nodes[video_id]['genre']

            # Update atau inisialisasi weight pada edge
            if not self.graph.has_edge(user_id, video_id):
                # Jika edge belum ada, tambahkan edge dengan inisialisasi weight
                self.graph.add_edge(user_id, video_id, weight=0)  # Inisialisasi weight di sini
            
            # Pastikan atribut weight ada sebelum menambahkan
            if 'weight' not in self.graph[user_id][video_id]:
                self.graph[user_id][video_id]['weight'] = 0
            
            self.graph[user_id][video_id]['weight'] += weight

            # Perbarui preferensi genre pengguna
            user_preferences = self.graph.nodes[user_id].setdefault('genre_preferences', {})
            user_preferences[genre] = user_preferences.get(genre, 0) + weight

            # Rehitung skor menggunakan PageRank
            self.recalculate_scores()
        else:
            print("Video not found.")

    def recalculate_scores(self):
        # Recalculate genre-based scores
        personalization = {
            video: self.graph.nodes[video]['initial_score']
            for video in self.videos
        }
        total_score = sum(personalization.values())

        # Normalize personalization for PageRank
        if total_score > 0:
            personalization = {k: v / total_score for k, v in personalization.items()}

        pagerank_scores = nx.pagerank(self.graph, weight='weight', personalization=personalization)

        for video_id, score in pagerank_scores.items():
            if video_id in self.graph.nodes and self.graph.nodes[video_id].get('type') == 'video':
                self.graph.nodes[video_id]['current_score'] = score

    def for_your_page(self, user_id, top_k=5):
        if user_id not in self.graph:
            return []

        # Recalculate scores to ensure they are up-to-date
        self.recalculate_scores()

        # Get user genre preferences
        user_preferences = self.graph.nodes[user_id].get('genre_preferences', {})

        # Generate recommendations
        recommendations = sorted(
            (
                (node, self.graph.nodes[node].get('current_score', 0) * (1 + user_preferences.get(self.graph.nodes[node].get('genre'), 0) / 10))
                for node in self.videos
            ),
            key=lambda x: x[1],
            reverse=True
        )

        # Update edges for recommendation visualization
        for video, score in recommendations:
            if not self.graph.has_edge(user_id, video):
                self.graph.add_edge(user_id, video, recommendation_score=score)

        return recommendations[:top_k]

def display_score(video_data):
    print("\n" + "="*40)
    print(f"🎬 Now Playing: {video_data['title']}")
    print(f"Genre: {video_data['genre']}")
    print(f"Viewers: {video_data['viewers']}")
    print(f"Likes: {video_data['likes']} | Comments: {video_data['comments']} | Shares: {video_data['shares']} | Saves: {video_data['saves']}")
    print("="*40)

def visualize_graph(graph):
    pos = nx.spring_layout(graph)
    plt.figure(figsize=(12, 8))

    node_colors = []
    node_labels = {}
    for node, data in graph.nodes(data=True):
        if data['type'] == 'user':
            node_colors.append('blue')
            node_labels[node] = node  # ID User
        elif data['type'] == 'video':
            node_colors.append('green')
            node_labels[node] = node  # ID Video

    # Weight
    edge_weights = []
    edge_labels = {}
    for u, v, data in graph.edges(data=True):
        score = data.get('recommendation_score', data.get('weight', 0))  # Use Score
        edge_weights.append(score)
        edge_labels[(u, v)] = f"{score:.4f}" 

    # GNode
    nx.draw_networkx_nodes(
        graph, pos,
        node_size=500,
        node_color=node_colors,
    )

    # Edge
    nx.draw_networkx_edges(
        graph, pos,
        width=[(w / max(edge_weights)) * 5 for w in edge_weights] if edge_weights else 1,
        alpha=0.6,
    )

    # Node label
    nx.draw_networkx_labels(graph, pos, labels=node_labels)

    # Edge label
    nx.draw_networkx_edge_labels(
        graph, pos,
        edge_labels=edge_labels,
        font_size=8,
    )

    plt.title("TikTok FYP Interaction Graph with Updated Scores")
    plt.axis("off")
    plt.show()

def main():
    fyp = TikTokFYP("video_dataset.csv")  
    user_id = "user_1"
    fyp.add_user(user_id)
    fyp.calculate_initial()

    while True:
        print("\n🕺💃 TikTok For You Page 🕺💃")
        print("1. Next Video")
        print("2. See FYP List")
        print("3. Visualize Graph")
        print("4. Exit")
        
        choice = input("Choose options (1/2/3/4): ")

        if choice == "1":
            recommendations = fyp.for_your_page(user_id, top_k=len(fyp.videos))
            
            if recommendations:
                videos, scores = zip(*recommendations)
                video_choice = random.choices(videos, weights=scores, k=1)[0]
            else:
                video_choice = random.choice(fyp.videos)
                
            video_data = fyp.graph.nodes[video_choice]
            display_score(video_data)
            watch_full = input("Watch this? (Full/Half/Skip): ").strip().lower()     
            if watch_full in ["full", "half"]:
                full_watch = 1 if watch_full == "full" else 0.5
                print("\nInteract with this video!")
                like = int(input("Like? (1 for Yes, 0 for No): "))
                comment = int(input("Comment? (1 for Yes, 0 for No): "))
                share = int(input("Share? (1 for Yes, 0 for No): "))
                saves = int(input("Save? (1 for Yes, 0 for No): "))
                fyp.interact_with_video(user_id, video_choice, like=like, comment=comment, share=share, saves=saves, full_watch=full_watch)
            print(f"Interaction with {video_data['title']} video recorded!")

        elif choice == "2":
            print("\n📱 For Your Page Video Ranking 📱")
            recommendations = fyp.for_your_page(user_id)
            for video, score in recommendations:
                video_data = fyp.graph.nodes[video]
                display_score(video_data)
                print(f"Score: {score:.4f}\n")

        elif choice == "3":
            fyp.recalculate_scores()
            visualize_graph(fyp.graph)

        elif choice == "4":
            print("Thank you!")
            break

        else:
            print("Not valid choice.")

if __name__ == "__main__":
    main()