import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import '../models/models.dart';

class LocalDb {
  static final LocalDb _instance = LocalDb._internal();
  static Database? _database;

  factory LocalDb() => _instance;

  LocalDb._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDb();
    return _database!;
  }

  Future<Database> _initDb() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'shemsu_shop_db.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE cart_items (
            name TEXT PRIMARY KEY,
            price REAL NOT NULL,
            qty INTEGER NOT NULL,
            isCustom INTEGER NOT NULL,
            comment TEXT NOT NULL
          )
        ''');
      },
    );
  }

  Future<List<CartItem>> getCartItems() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query('cart_items');

    return List.generate(maps.length, (i) {
      return CartItem.fromJson(maps[i]);
    });
  }

  Future<void> insertItem(CartItem item) async {
    final db = await database;
    await db.insert(
      'cart_items',
      item.toJson(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<void> updateItem(CartItem item) async {
    final db = await database;
    await db.update(
      'cart_items',
      item.toJson(),
      where: 'name = ?',
      whereArgs: [item.name],
    );
  }

  Future<void> deleteItem(String name) async {
    final db = await database;
    await db.delete(
      'cart_items',
      where: 'name = ?',
      whereArgs: [name],
    );
  }

  Future<void> clearCart() async {
    final db = await database;
    await db.delete('cart_items');
  }
}
