import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:async';
import 'package:camera/camera.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final cameras = await availableCameras();
  final firstCamera = cameras.first;

  runApp(MyApp(camera: firstCamera));
}

// A screen that allows users to take a picture using a given camera.
class MyApp extends StatefulWidget {
  const MyApp({
    Key? key,
    required this.camera,
  }) : super(key: key);

  final CameraDescription camera;

  @override
  MyAppState createState() => MyAppState();
}

class MyAppState extends State<MyApp> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    _initializeControllerFuture = _controller.initialize();
  }

  @override
  void dispose() async {
    await _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    Widget cameraPreview = Container(
      child: GestureDetector(
        onTap: () async {
          try {
            await _initializeControllerFuture;
            final image = await _controller.takePicture();
            var request = http.MultipartRequest(
                "POST", Uri.parse("http://192.168.1.2:5000/"));
            request.files.add(await http.MultipartFile.fromPath(
                "image", image.path,
                contentType: MediaType("image", "jpeg")));
            var response = await request.send();
          } catch (e) {
            print('test :)');
          }
        },
        child: FutureBuilder<void>(
          future: _initializeControllerFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.done) {
              var size = MediaQuery.of(context).size.width * 0.75;
              return Center(
                child: Container(
                  width: size,
                  height: size,
                  decoration: BoxDecoration(
                    boxShadow: [
                      BoxShadow(
                        color: Colors.grey.withOpacity(0.5),
                        spreadRadius: 5,
                        blurRadius: 7,
                        offset: const Offset(0, 2), // changes position of shadow
                      ),
                    ],
                  ),
                  child: ClipRect(
                    child: OverflowBox(
                      alignment: Alignment.center,
                      child: FittedBox(
                        fit: BoxFit.fitWidth,
                        child: Container(
                          width: size,
                          height: size * _controller.value.aspectRatio,
                          child: CameraPreview(_controller),
                        ),
                      ),
                    ),
                  ),
                )
              );
            } else {
              return const Center(child: CircularProgressIndicator());
            }
          },
        )
      )
    );

    return MaterialApp(
      title: 'OutSmarted',
      theme: ThemeData(
        scaffoldBackgroundColor: Color.fromARGB(233, 233, 242, 255),
      ),
      home: Scaffold(
        appBar: AppBar(
          leading: const Icon(
            Icons.camera_alt,
            color: Color.fromARGB(233, 122, 168, 231),
          ),
          title: const Text('OutSmarted')
          ),
        body: Column(
          children: [
            Container(
              margin: const EdgeInsets.fromLTRB(0, 16, 0, 4),
              child: const Text('Tap to scan a Game'),
            ),
            cameraPreview,
            Container(
              margin: const EdgeInsets.fromLTRB(0, 14, 0, 0),
              width: 300,
              child: Image.asset('assets/images/tictactoe.png'),
            ),
            Center(
              child: Container(
                margin: const EdgeInsets.fromLTRB(0, 8, 0, 0),
                child: InkWell(
                  child: const Text(
                    'GitHub',
                    style: TextStyle(
                      decoration: TextDecoration.underline,
                      decorationColor: Color.fromARGB(255, 96, 102, 116),
                      color: Color.fromARGB(255, 96, 102, 116),
                    ),
                  ),
                  onTap: () => launch('https://github.com/foersterrobert/OutSmarted'),
                ),
              )
            ),
          ],
        ),
      )
    );
  }
}
