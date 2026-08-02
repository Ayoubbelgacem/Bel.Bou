import 'package:highlight/highlight.dart';

final Mode tounsilang = Mode(
  className: 'tounsilang',
  keywords: {
    'keyword': [
      // Variables / contrôle
      'khdem',
      'khedm',
      'ken',
      'sinon',
      'sinon_ken',
      'a3mel',
      'men',
      '7ata',
      'hatta',
      'tawa',
      // OOP
      'class',
      'toroth',
      'hetha',
      'jdid',
      'super',
      'new',
      // Try/catch
      '7awel',
      'ebsed',
      'akhir',
      // Import
      'jib',
      // Contrôle de boucle
      'wakaf',
      'tkhata',
      // Littéraux booléens
      's7i7',
      'ghalet',
    ],
    'built_in': [
      'ikteb',
      'iqra',
      'iqra_mlf',
      'ikteb_fi_mlf',
      'len',
      'type',
      'str',
      'int',
      'float',
      'time_now',
      'sleep',
      'rqed',
      'to_json',
    ],
    'function': [
      'dallel',
      'fonction',
      'rejje',
      'retourner',
    ],
  },
  contains: [
    // Chaînes doubles
    Mode(className: 'string', begin: '"', end: '"'),
    // Chaînes simples
    Mode(className: 'string', begin: "'", end: "'"),
    // Commentaires
    Mode(className: 'comment', begin: '#', end: r'$'),
    Mode(className: 'comment', begin: '//', end: r'$'),
    Mode(className: 'comment', begin: r'/\*', end: r'\*/'),
    // Nombres
    Mode(className: 'number', begin: r'\b\d+(\.\d+)?\b'),
  ],
);
