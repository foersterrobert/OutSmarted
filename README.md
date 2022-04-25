# OutSmarted
![outSmarted](outsmarted.png)

### Nächste Schritte
- MiniMax Optimierung + Connect-Four-DQN (Simon +/ Jesper)
- synthetischer Datensatz in Blender | TicTacToe + Connect-Four (Anjo +/ Robert)

#### Yolo-Model für TicTacToe: [GoogleDrive](https://drive.google.com/file/d/17TLUq98AcpB5d1u1_gxL9Cehq-rfpF_i/view?usp=sharing) &rarr; Git LFS

```
flutter run --release
```

- 🐛 Die Kamera friert ein, sobald die App länger im Hintergrund ist. (statelifecycle in Flutter)

### BW-KI
Titel: OutSmarted

Idee:
Wir bauen eine Smartphone-App, die über die Kamera Brettspiele scannen kann. Sobald das Spiel selbst und sein State erkannt wurde, wird das die optimale Spielverhalten zurückgegeben. Für das Frontend nutzen wir Flutter um die App möglichst schnell in Android und iOS zu veröffentlichen. Sobald die Nutzer:in ein Foto gemacht hat wird dieses direkt mit einer push-Request an unseren Backend-Server geschickt. Hier nutzen wir das Python-Framework Flask. Im ersten Schritt erkennt ein ConvNet-Klassifizierungs-Modell das Spiel, um das es sich auf dem Bild handelt. Für den Anfang sind als Klassen TicTacToe, Connect-Four & Chess geplant. Jetzt kann die Nutzer:in abhängig vom Spiel auswählen, ob sie Spieler:in 1 oder Spieler:in 2 ist. Basierend auf dieser Entscheidung berechnet ein auf das Spiel angepasstes YOLO-object-detection-Modell, den State des Spieles. Der erhaltene State und die ausgewählte Spieler:in wird dann genutzt um den perfekten Zug zurückzugeben. Für TicTacToe nutzen wir dafür den MiniMax-Algorithmus mit Alpha-Beta-Pruning, für Connect-Four ein erweitertes DQN und für Chess voraussichtlich MuZero. Der State und der Zug wird anschließend im Frontend visualisiert.

Daten:
Für die Klassifizierung des Spiels und vor allem die Erkennung des States über object-detection brauchen wir hunderttausende annotierte Fotos. Für TicTacToe haben wir bereits einen ausreichenden Datensatz mit handgezeichneten Spielen zum einen selbst erstellt und zum anderen von Kaggle https://www.kaggle.com/datasets/cashlol/tictactoe-ox-cropped Essientiell ist hierbei die nachträgliche Augmentierung übers spiegeln, rotieren und vorallem das zufällige hinzufügen von Effekten wie die veränderung der Helligkeit oder der Farbe. Somit können wir unseren Datensatz vertausendfachen. Für Connect-Four und Chess erstellen wir unsere Daten synthetisch über ein Script in Blender. Nur so können wir die große Bandbreite an unterschiedlichen Spielbrettern und Hintergrundkontexten abdecken. Sollten wir für Chess MuZero implementieren brauchen wir, da es sich um einen model-based reinforcement-learning Algorithmus handelt, zusätzlich unzählige Chess-Moves auf Profi-Niveau. Hierfür würden wir die http://caissabase.co.uk/ Datenbank nutzen.
