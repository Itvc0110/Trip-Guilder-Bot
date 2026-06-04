import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "travel.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create spots table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        address TEXT NOT NULL,
        rating REAL NOT NULL,
        review_count INTEGER NOT NULL,
        vibe TEXT NOT NULL, -- romantic, active, food
        tags TEXT NOT NULL, -- comma-separated tags
        open_hours TEXT NOT NULL,
        crowd_level INTEGER DEFAULT 0, -- number of planned visits at current time
        price_range TEXT NOT NULL, -- $, $$, $$$
        description TEXT NOT NULL,
        images TEXT DEFAULT '[]', -- JSON array of image URLs from Google Maps
        data_id TEXT -- Google Maps data_id for fetching detailed info
    )
    """)
    
    # Create event_logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS event_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
        event_type TEXT NOT NULL,
        spot_id INTEGER,
        old_time_slot TEXT,
        new_time_slot TEXT,
        reason TEXT,
        vibe TEXT,
        num_people INTEGER
    )
    """)
    
    # Seed data
    cursor.execute("SELECT COUNT(*) FROM spots")
    if cursor.fetchone()[0] == 0:
        seed_data = [
            # --- ROMANTIC (Lãng mạn & Riêng tư) ---
            ("Cafe Yên Dang Thai Mai", 21.0712, 105.8235, "11A Ngõ 82/18 Yên Phụ, Tây Hồ", 4.7, 850, "romantic", "cafe, cozy, lakeside", "07:30 - 21:00", 8, "$$", "Quán cà phê mộc mạc với khoảng sân vườn yên bình, nổi tiếng với món Sapa Coffee thơm ngậy, rất thích hợp cho những buổi trò chuyện nhỏ của hai người."),
            ("Skyline Hanoi Rooftop", 21.0345, 105.8530, "38 Gia Ngư, Hoàn Kiếm", 4.5, 620, "romantic", "restaurant, bar, view_ho, upscale", "11:00 - 23:00", 12, "$$$", "Quán bar nhà hàng tầng thượng sang trọng với view ngắm toàn cảnh phố cổ và hồ Gươm từ trên cao. Cực kỳ lãng mạn vào thời điểm hoàng hôn."),
            ("Nhà thờ Lớn Hà Nội (St. Joseph's Cathedral)", 21.0287, 105.8490, "40 Nhà Chung, Hoàn Kiếm", 4.6, 3200, "romantic", "stroll, landmark, photo", "08:00 - 21:00", 18, "$", "Địa điểm dạo bộ, chụp ảnh đôi kinh điển xung quanh nhà thờ kiến trúc Gothic cổ kính. Buổi tối có thể ngồi trà chanh ngắm phố."),
            ("Chùa Trấn Quốc & Đường Thanh Niên", 21.0480, 105.8360, "Đường Thanh Niên, Tây Hồ", 4.5, 4500, "romantic", "stroll, landmark, sunset", "08:00 - 18:00", 15, "$", "Ngôi chùa cổ nhất Hà Nội nằm bên bán đảo hồ Tây thơ mộng. Dạo bước ngắm hoàng hôn dọc đường Thanh Niên là hoạt động hẹn hò yêu thích của nhiều thế hệ."),
            ("Bến Hàn Quốc Tây Hồ", 21.0690, 105.8280, "Cuối ngõ 399 Âu Cơ, Tây Hồ", 4.3, 1200, "romantic", "stroll, view_ho, budget", "24/7", 22, "$", "Đường ven hồ Tây thanh bình lộng gió, nơi các cặp đôi thường tới ngắm hoàng hôn, tâm sự và chụp ảnh với view mặt nước thoáng đãng."),
            ("Maison de Tet Decor", 21.0655, 105.8210, "26 Quảng An, Tây Hồ", 4.4, 450, "romantic", "cafe, brunch, lakeside", "08:00 - 22:00", 6, "$$", "Ngôi biệt thự Pháp cổ màu vàng nghệ độc đáo ven hồ Tây, không gian yên tĩnh mang đậm chất nghệ thuật, phục vụ đồ uống sạch và đồ ăn brunch healthy."),
            ("Hồ Tây lộng gió (Trích Sài)", 21.0545, 105.8080, "Đường Trích Sài, Tây Hồ", 4.5, 9800, "romantic", "stroll, view_ho", "24/7", 25, "$", "Trục đường đi dạo, đạp xe đôi ven hồ rộng nhất Hà Nội, ngắm trọn vẹn hoàng hôn buông xuống mặt nước."),
            ("Cầu Long Biên cổ kính", 21.0435, 105.8560, "Cầu Long Biên, Hoàn Kiếm/Long Biên", 4.6, 5200, "romantic", "stroll, photo, historical", "24/7", 14, "$", "Cây cầu lịch sử trăm tuổi, nơi ngắm bình minh hoặc hoàng hôn lãng mạn dọc đường ray xe lửa cũ, đón những làn gió mát lành từ sông Hồng."),
            ("Công viên Bách Thảo Hà Nội", 21.0392, 105.8315, "1 Hoàng Hoa Thám, Ba Đình", 4.4, 2100, "romantic", "park, stroll, nature", "06:00 - 22:00", 5, "$", "Khu rừng nhỏ giữa lòng thủ đô với những cây cổ thụ trăm tuổi, hồ nước nhỏ và đàn bồ câu thân thiện. Không gian tĩnh lặng lý tưởng để cặp đôi tản bộ tránh ồn ào."),
            ("Woodland Cozy Lounge", 21.0265, 105.8450, "15 Ngõ Bà Triệu, Hai Bà Trưng", 4.6, 310, "romantic", "bar, cozy, private", "18:00 - 01:00", 4, "$$", "Không gian lounge ấm cúng với tông màu gỗ trầm, ánh đèn vàng mờ và nhạc jazz êm dịu, mang lại không gian trò chuyện cực kỳ riêng tư cho buổi tối hẹn hò."),
            ("Sunset Bar - InterContinental", 21.0592, 105.8310, "5 Từ Hoa, Tây Hồ", 4.7, 720, "romantic", "bar, view_ho, luxury", "16:00 - 23:30", 9, "$$$", "Quán bar nằm hoàn toàn trên mặt nước hồ Tây, kết nối bằng những cây cầu gỗ lung linh ánh đèn. Trải nghiệm ngắm hoàng hôn thượng hạng."),
            ("Labri - Bistro Oriental", 21.0330, 105.8475, "113 Bùi Thị Xuân, Hai Bà Trưng", 4.8, 280, "romantic", "restaurant, dinner, private", "17:30 - 22:30", 3, "$$$", "Nhà hàng Pháp-Á nhỏ xinh tinh tế với phong cách bài trí tối giản lãng mạn, menu đổi mới liên tục theo mùa thích hợp cho ngày kỷ niệm."),
            ("Cửa Hàng Ăn Tập Thể Mậu Dịch", 21.0360, 105.8420, "37 Nam Tràng, Ba Đình", 4.2, 540, "romantic", "restaurant, dinner, nostalgic", "10:00 - 22:00", 11, "$$", "Không gian ẩm thực tái hiện thời kỳ bao cấp độc đáo, ấm cúng và đầy hoài niệm."),
            ("Cư Xá Cà Phê - Láng Hạ", 21.0180, 105.8140, "Tập thể C1C Láng Hạ, Đống Đa", 4.4, 670, "romantic", "cafe, nostalgic, cozy", "09:00 - 22:30", 7, "$", "Quán cà phê nằm trong khu tập thể cũ với ban công lộng gió, những món quà vặt tuổi thơ khơi gợi những câu chuyện xưa cũ."),
            ("Rêu Coffee & Tea", 21.0495, 105.7950, "5 Ngõ 106 Hoàng Quốc Việt, Cầu Giấy", 4.5, 190, "romantic", "cafe, cozy, hidden", "08:00 - 22:00", 2, "$", "Quán cà phê ẩn mình sâu trong ngõ nhỏ, ngập tràn rêu xanh phong rêu và cây xanh tĩnh mịch."),
            ("Bình Minh Jazz Club", 21.0252, 105.8568, "1 Tràng Tiền, Hoàn Kiếm", 4.6, 920, "romantic", "bar, jazz, livemusic", "17:00 - 24:00", 6, "$$$", "Câu lạc bộ nhạc Jazz trực tiếp huyền thoại tại Hà Nội của nghệ sĩ Quyền Văn Minh. Không gian mờ ảo lãng mạn."),
            ("La Badiane", 21.0270, 105.8445, "10 Nam Ngư, Hoàn Kiếm", 4.7, 490, "romantic", "restaurant, fine_dining", "11:30 - 22:30", 4, "$$$", "Nhà hàng Pháp ẩm thực đỉnh cao nằm trong ngõ nhỏ yên tĩnh biệt lập, kiến trúc giếng trời thanh lịch tràn ngập ánh sáng."),
            ("Trill Rooftop Cafe", 21.0015, 105.7985, "Tòa nhà Hei Tower, Thanh Xuân", 4.3, 1850, "romantic", "cafe, view_city, photo", "08:00 - 23:00", 16, "$$", "Quán cà phê sân thượng có hồ bơi ngoài trời, lộng gió và ngắm nhìn toàn cảnh phía Tây Hà Nội lung linh ánh đèn về đêm."),
            ("The Loading T Cafe", 21.0315, 105.8495, "8 Chân Cầm, Hoàn Kiếm", 4.6, 580, "romantic", "cafe, cozy, historic", "08:00 - 22:00", 5, "$$", "Nằm trong tòa biệt thự Pháp cổ lộng lẫy trên phố Chân Cầm, gạch hoa xưa cũ, hương quế thoang thoảng và nhạc Trịnh du dương."),
            ("L'Amant Cafe", 21.0298, 105.8540, "10 Nguyễn Hữu Huân, Hoàn Kiếm", 4.4, 210, "romantic", "cafe, cozy, historic", "07:00 - 22:30", 6, "$$", "Quán cafe phong cách Đông Dương xưa, không gian nhỏ gọn ấm cúng, nhạc không lời êm ái cho cuộc trò chuyện."),
            
            # --- ACTIVE (Năng động & Trải nghiệm mới) ---
            ("Complex 01 Đống Đa", 21.0185, 105.8250, "Số 29 ngách 31 ngõ 167 Tây Sơn, Đống Đa", 4.6, 1200, "active", "complex, workshop, photogenic", "08:00 - 22:00", 28, "$$", "Tổ hợp văn hóa, nghệ thuật được cải tạo từ nhà máy cũ. Nơi tổ chức nhiều workshop làm gốm, thêu thùa, nến thơm và các sự kiện âm nhạc, hội chợ cuối tuần."),
            ("Lotte Mall West Lake Aqua Arena", 21.0735, 105.8130, "272 Võ Chí Công, Tây Hồ", 4.7, 4200, "active", "entertainment, workshop, shopping", "09:30 - 22:00", 35, "$$$", "Thủy cung trong nhà quy mô lớn nhất thủ đô nằm tại Lotte Mall, kèm rạp chiếu phim chất lượng cao và khu vui chơi hiện đại cho buổi hẹn năng động."),
            ("Royal City Ice Rink", 21.0028, 105.8150, "B2 Royal City, 72A Nguyễn Trãi, Thanh Xuân", 4.4, 2100, "active", "skating, sports", "09:30 - 22:00", 22, "$$", "Sân trượt băng thật đầu tiên và lớn nhất Việt Nam. Trải nghiệm dắt tay nhau trượt băng vô cùng thú vị và tăng cường tương tác."),
            ("Bảo tàng Dân tộc học Việt Nam", 21.0405, 105.8010, "Nguyễn Văn Huyên, Cầu Giấy", 4.7, 5600, "active", "museum, stroll, photo", "08:30 - 17:30", 9, "$", "Khuôn viên ngoài trời rộng mát với các nhà rông, nhà sàn mô hình. Đi tản bộ khám phá và chụp hình phong cách dã ngoại cực thú vị."),
            ("Tổ hợp Vui chơi Creative City", 21.0152, 105.8612, "1 Lương Yên, Hai Bà Trưng", 4.1, 750, "active", "complex, gaming, art", "08:30 - 22:00", 14, "$$", "Khu tổ hợp nghệ thuật sáng tạo với phòng tranh graffiti, leo núi trong nhà, các tiệm đồ handmade độc đáo."),
            ("Leo núi trong nhà VietClimb", 21.0450, 105.8260, "40 Ngõ 76 An Dương, Tây Hồ", 4.5, 340, "active", "sports, fitness", "09:00 - 22:00", 4, "$$", "Thử thách leo núi đá thể thao trong nhà, một hoạt động phối hợp tuyệt vời giúp cặp đôi gắn kết đồng đội và rèn luyện thể lực."),
            ("Bắn cung thể thao Target Archery", 21.0210, 105.7820, "Ngõ 79 Cầu Giấy, Cầu Giấy", 4.4, 210, "active", "sports, archery", "09:00 - 21:00", 6, "$$", "Trải nghiệm học bắn cung cơ bản cho cặp đôi, cạnh tranh lành mạnh xem ai bắn trúng tâm nhiều hơn."),
            ("Jump Arena Tang Bat Ho", 21.0185, 105.8580, "1 Tăng Bạt Hổ, Hai Bà Trưng", 4.5, 1100, "active", "sports, entertainment", "09:00 - 21:00", 15, "$$", "Khu vui chơi bạt nhún nhào lộn trampoline vô cùng sảng khoái và tràn đầy tiếng cười giải tỏa căng thẳng đầu óc."),
            ("Lớp làm bánh gato Cake Craft", 21.0212, 105.8190, "12 Ngõ 19 Láng Hạ, Ba Đình", 4.6, 120, "active", "workshop, cooking, sweet", "09:00 - 18:00", 3, "$$$", "Workshop tự làm bánh kem và trang trí bánh đôi độc đáo mang về, tự tay gửi gắm yêu thương qua hương vị ngọt ngào."),
            ("Xưởng gốm Bát Tràng Moment", 21.0310, 105.8450, "12 Ngõ Tràng An, Hoàn Kiếm", 4.7, 180, "active", "workshop, art, pottery", "09:00 - 19:30", 8, "$$", "Chi nhánh lớp trải nghiệm vuốt nặn gốm xoay Bát Tràng ngay trung tâm phố cổ, tự tay tạo hình chiếc ly, chiếc bát kỷ niệm."),
            ("Học làm nến thơm Chill Candle", 21.0322, 105.8035, "28 Ngõ 294 Kim Mã, Ba Đình", 4.7, 95, "active", "workshop, fragrance", "10:00 - 20:30", 2, "$$$", "Tự phối hương thơm tinh dầu, đổ sáp nến hoa khô làm quà tặng ý nghĩa cho đối phương trong không gian đầy thư giãn."),
            ("Bảo tàng Mỹ thuật Việt Nam", 21.0305, 105.8398, "66 Nguyễn Thái Học, Ba Đình", 4.6, 2300, "active", "museum, art, photo", "08:30 - 17:00", 8, "$", "Nơi trưng bày vô vàn tác phẩm nghệ thuật, tranh sơn mài đỉnh cao quốc gia, kiến trúc thuộc địa Pháp cổ cực kỳ ăn ảnh."),
            ("Hồ Gươm đi bộ cuối tuần", 21.0285, 105.8522, "Quanh Hồ Hoàn Kiếm, Hoàn Kiếm", 4.7, 54000, "active", "stroll, street_performance, night", "19:00 thứ 6 - 24:00 chủ nhật", 45, "$", "Tuyến phố đi bộ sầm uất với các hoạt động âm nhạc đường phố nhảy múa, trò chơi dân gian rộn ràng về đêm."),
            ("Rạp phim giường nằm L'amour", 21.0375, 105.8155, "CGV Vincom Nguyễn Chí Thanh, Đống Đa", 4.5, 480, "active", "movie, luxury, cozy", "09:00 - 24:00", 5, "$$$", "Phòng chiếu phim giường nằm cao cấp ấm cúng kèm nước uống và đồ ăn nhẹ miễn phí cho ngày lười dạo phố."),
            ("Trò chơi nhập vai Lost Escape Room", 21.0318, 105.8512, "50 Nguyễn Hữu Huân, Hoàn Kiếm", 4.6, 420, "active", "gaming, puzzle", "09:00 - 22:30", 4, "$$", "Thử thách giải đố, mở khóa thoát phòng cùng nhau vô cùng kịch tính kích thích tư duy đồng đội."),
            ("Tiệm Boardgame Dice & Cafe", 21.0225, 105.8230, "79 Ngõ 298 Tây Sơn, Đống Đa", 4.4, 290, "active", "cafe, boardgame", "09:00 - 22:30", 12, "$", "Hàng trăm tựa game thẻ bài từ dễ đến khó để cặp đôi giải trí hoặc giao lưu nhóm cùng nhau."),
            ("Xưởng Tranh tự vẽ Tipsy Art", 21.0268, 105.8488, "B5 Ngõ Nguyễn Du, Hai Bà Trưng", 4.8, 380, "active", "workshop, art, painting", "09:00 - 17:30", 3, "$$$", "Lớp học vẽ tranh canvas cơ bản có giáo viên hướng dẫn tỉ mỉ, thư thái nhâm nhi trà bánh trong lúc tô màu."),
            ("Chèo SUP Hồ Tây lúc bình minh", 21.0585, 105.8195, "292 Lạc Long Quân, Tây Hồ", 4.5, 540, "active", "sports, water, adventure", "05:00 - 08:00, 16:00 - 18:30", 7, "$$", "Trải nghiệm chèo ván đứng lướt sóng đón những tia nắng bình minh dịu mát trên mặt hồ rộng nhất Hà Nội."),
            ("Học làm nước hoa tự chế L'Organs", 21.0350, 105.8340, "Ngõ 135 Đội Cấn, Ba Đình", 4.7, 75, "active", "workshop, fragrance", "09:00 - 18:00", 2, "$$$", "Tự tay điều chế dòng nước hoa signature mang đậm dấu ấn cá nhân của chính mình dành tặng đối phương."),
            ("VR Game Zone - Lotte Center", 21.0318, 105.8122, "Tầng 5 Lotte Center, 54 Liễu Giai, Ba Đình", 4.4, 510, "active", "gaming, tech", "09:30 - 22:00", 10, "$$", "Trải nghiệm kính thực tế ảo hiện đại nhập vai tàu lượn siêu tốc hoặc chiến đấu đồng đội kịch tính."),
            
            # --- FOOD (Ẩm thực & Phố xá) ---
            ("Cafe Giảng - Cafe Trứng", 21.0383, 105.8541, "39 Nguyễn Hữu Huân, Hoàn Kiếm", 4.5, 5400, "food", "cafe, local_food, classic", "07:00 - 22:00", 32, "$", "Quán cà phê trứng huyền thoại lâu đời bậc nhất Hà Nội, hương vị kem trứng béo ngậy thơm nức lòng du khách và người bản địa."),
            ("Phở Thìn Lò Đúc", 21.0205, 105.8560, "13 Lò Đúc, Hai Bà Trưng", 4.2, 4200, "food", "local_food, lunch, classic", "06:00 - 20:30", 28, "$", "Món phở bò tái lăn xào tỏi ngập hành nổi tiếng, hương vị nước dùng đậm đà làm nức lòng thực khách nhiều thập kỷ."),
            ("Bánh cuốn bà Hoành Tô Hiến Thành", 21.0182, 105.8492, "66 Tô Hiến Thành, Hai Bà Trưng", 4.3, 2100, "food", "local_food, breakfast", "06:00 - 20:00", 15, "$", "Bánh cuốn Thanh Trì mỏng dai ăn kèm chả mỡ béo ngậy và nước chấm pha ấm nóng đậm đà cổ truyền."),
            ("Bún chả Hương Liên (Bun Cha Obama)", 21.0195, 105.8548, "24 Lê Văn Hưu, Hai Bà Trưng", 4.2, 8500, "food", "local_food, lunch, historic", "08:00 - 20:30", 35, "$$", "Địa điểm nổi tiếng từng tiếp đón cựu tổng thống Mỹ Barack Obama, bún chả thơm lừng vị nướng than hoa."),
            ("Chả cá Lã Vọng Nguyễn Trường Tộ", 21.0442, 105.8428, "14 Nguyễn Trường Tộ, Ba Đình", 4.4, 3200, "food", "local_food, dinner, historic", "09:00 - 22:00", 16, "$$$", "Món chả cá lăng nướng chảo mỡ sôi xèo xèo ăn kèm hành thì là, mắm tôm và lạc rang mang đậm hương vị kinh kỳ."),
            ("Kem Tràng Tiền", 21.0252, 105.8550, "35 Tràng Tiền, Hoàn Kiếm", 4.5, 18500, "food", "sweet, stroll, iconic", "08:00 - 23:00", 42, "$", "Thưởng thức kem que đậu xanh, cốm, dừa truyền thống rồi đi dạo quanh hồ Gươm lộng gió là thói quen thư giãn kinh điển."),
            ("Bánh gối Lý Quốc Sư", 21.0292, 105.8488, "52 Lý Quốc Sư, Hoàn Kiếm", 4.1, 1400, "food", "local_food, street_food", "09:00 - 21:30", 19, "$", "Quán ăn vặt lâu đời nổi tiếng với vỏ bánh gối giòn tan, nhân thịt mộc nhĩ nóng hổi ăn kèm nước chấm chua ngọt dưa góp."),
            ("Bún đậu mắm tôm ngõ Tràng Tiền", 21.0250, 105.8540, "Ngõ Tràng Tiền, Hoàn Kiếm", 4.3, 950, "food", "local_food, street_food", "09:00 - 15:00", 25, "$", "Mẹt bún đậu đầy đặn giòn rụm trong con ngõ nhỏ ngay trung tâm, đặc trưng bởi bát mắm tôm pha chanh ớt sủi bọt thơm lừng."),
            ("Ốc nóng Hà Trang Đinh Liệt", 21.0335, 105.8525, "1 Đinh Liệt, Hoàn Kiếm", 4.3, 1100, "food", "local_food, street_food, night", "15:00 - 22:30", 24, "$$", "Hàng ốc luộc lá chanh giòn ngọt ăn kèm nước chấm gừng sả ớt đặc trưng cay nồng sưởi ấm những chiều lộng gió."),
            ("Nộm bò khô Long Vi Dung", 21.0315, 105.8530, "23 Hồ Hoàn Kiếm, Hoàn Kiếm", 4.2, 1800, "food", "local_food, street_food", "08:30 - 22:30", 26, "$", "Đĩa nộm đu đủ bò khô truyền thống đầy đặn ngay cạnh hồ Gươm, vị chua ngọt cay giòn hấp dẫn."),
            ("Bánh mì sốt vang Đình Ngang", 21.0298, 105.8415, "252 Hàng Bông (Đầu Đình Ngang), Hoàn Kiếm", 4.2, 1200, "food", "local_food, dinner", "15:00 - 23:30", 18, "$", "Bát sốt vang gân bò mềm thơm phức nóng hổi chấm bánh mì giòn rụm cực kỳ thích hợp cho bữa tối muộn."),
            ("Nem chua nướng em Phượng Ấu Triệu", 21.0285, 105.8485, "10 Ấu Triệu, Hoàn Kiếm", 4.3, 1600, "food", "local_food, street_food, night", "14:00 - 23:30", 28, "$", "Nem chua nướng cháy xèo trên than hồng đặt trên khay lót lá chuối xanh, chấm tương ớt đặc sản cay nồng."),
            ("Phở cuốn Hương Mai Ngũ Xã", 21.0475, 105.8390, "25 Ngũ Xã, Ba Đình", 4.3, 3100, "food", "local_food, lunch, view_lake", "09:00 - 22:00", 22, "$$", "Các cuộn bánh phở bò xào rau cải chấm nước mắm thanh mát cùng món phở chiên phồng độc đáo bên hồ Trúc Bạch."),
            ("Xôi Yến Nguyễn Hữu Huân", 21.0332, 105.8540, "35B Nguyễn Hữu Huân, Hoàn Kiếm", 4.0, 4800, "food", "local_food, heavy", "06:00 - 23:30", 29, "$$", "Hàng xôi xéo dẻo thơm ngập mỡ hành ăn kèm thịt kho, chả, trứng ốp khổng lồ nạp năng lượng cho ngày dài khám phá."),
            ("Bánh mì Lành (Bánh mì pate)", 21.0375, 105.8425, "57 Phúc Tân, Hoàn Kiếm", 4.4, 210, "food", "local_food, budget", "06:00 - 22:00", 10, "$", "Pate tự làm thơm phức béo ngậy, bơ quét dày vỏ bánh nướng vàng giòn."),
            ("Tào phớ Nghĩa Tân Cầu Giấy", 21.0260, 105.7925, "Đối diện cổng chợ Nghĩa Tân, Cầu Giấy", 4.3, 1500, "food", "sweet, street_food, budget", "10:00 - 18:30", 15, "$", "Bát tào phớ thạch găng, trân châu dai giòn nước đường hoa bưởi thanh mát đánh tan cơn nóng."),
            ("Lẩu riêu cua sườn sụn Phó Đức Chính", 21.0428, 105.8440, "66 Phó Đức Chính, Ba Đình", 4.4, 980, "food", "local_food, dinner", "17:00 - 23:00", 20, "$$", "Nồi lẩu riêu cua bắp bò gạch vàng óng sườn sụn sần sật bốc khói nghi ngút cho ngày se lạnh."),
            ("Quán Nhỏ (Beer & Local food)", 21.0198, 105.8182, "18 Huỳnh Thúc Kháng, Đống Đa", 4.3, 850, "food", "dinner, beer, dynamic", "10:30 - 23:30", 16, "$$", "Không gian ăn nhậu bia hơi kết hợp món ăn đồng quê phong phú nhộn nhịp, thích hợp tụ họp trò chuyện năng động."),
            ("Trà chanh Nhà Thờ Lớn", 21.0285, 105.8492, "Phố Nhà Thờ, Hoàn Kiếm", 4.2, 5400, "food", "cafe, street_food, budget", "16:00 - 23:30", 35, "$", "Nhâm nhi ly trà chanh chua ngọt cắn hạt hướng dương ngắm dòng người dạo quanh quảng trường Cathedral lung linh về đêm."),
            ("Bột lọc, nộm Mai Hắc Đế", 21.0165, 105.8505, "25 Mai Hắc Đế, Hai Bà Trưng", 4.3, 310, "food", "street_food, sweet", "14:00 - 19:30", 9, "$", "Bánh bột lọc dai vỏ đẫm nhân tôm thịt cùng nước chấm vừa miệng cho bữa ăn xế chiều nhẹ nhàng.")
        ]
        
        # We need to expand this list to reach ~80 curated items as planned.
        # Let's generate programmatic extensions based on real Hanoi spots so we get a massive seed DB
        # containing precisely 80 distinct curated places.
        extras = [
            # Extra Romantic (20 items to reach 40 romantic)
            ("Lưu Gia Trang Cafe", 21.0560, 105.8450, "Ngõ 264 Âu Cơ, Tây Hồ", 4.5, 150, "romantic", "cafe, nature", "08:00 - 22:00", 3, "$$"),
            ("Hanoi Social Club", 21.0298, 105.8475, "6 Hội Vũ, Hoàn Kiếm", 4.5, 820, "romantic", "cafe, music, hidden", "08:00 - 23:00", 5, "$$"),
            ("Cup of Tea Cafe", 21.0420, 105.7990, "109 Nguyễn Đình Hoàn, Cầu Giấy", 4.4, 380, "romantic", "cafe, view_river", "07:30 - 22:30", 4, "$$"),
            ("Rooftop Cafe Vincom", 21.0250, 105.8110, "54 Liễu Giai, Ba Đình", 4.5, 920, "romantic", "cafe, view_city", "08:00 - 22:30", 7, "$$"),
            ("Sora Cafe Garden", 21.0360, 105.8210, "12 Ngõ 9 Đặng Thai Mai, Tây Hồ", 4.6, 210, "romantic", "cafe, garden", "08:00 - 22:00", 2, "$$"),
            ("All Day Coffee Hàng Tre", 21.0315, 105.8560, "37 Hàng Tre, Hoàn Kiếm", 4.6, 950, "romantic", "cafe, cozy", "07:00 - 23:00", 9, "$$"),
            ("Blackbird Coffee", 21.0302, 105.8490, "5 Hân Siêu, Hoàn Kiếm", 4.5, 680, "romantic", "cafe, cozy", "07:00 - 21:30", 6, "$$"),
            ("Hidden Gem Cafe", 21.0385, 105.8520, "3B Hàng Tre, Hoàn Kiếm", 4.5, 410, "romantic", "cafe, recycled, unique", "08:00 - 23:00", 4, "$$"),
            ("Cafe de Flore", 21.0245, 105.8465, "95 Nguyễn Du, Hai Bà Trưng", 4.4, 320, "romantic", "cafe, photogenic", "07:30 - 22:00", 6, "$$"),
            ("Gạt Tàn Coffee", 21.0310, 105.8510, "11 Trần Huân, Hoàn Kiếm", 4.3, 180, "romantic", "cafe, hidden, vintage", "08:00 - 23:00", 3, "$"),
            ("Ban công Cafe Phố Cổ", 21.0340, 105.8515, "2 Đinh Liệt, Hoàn Kiếm", 4.5, 780, "romantic", "cafe, balcony, view_street", "07:00 - 23:00", 8, "$$"),
            ("Rooftop Bar Diamond", 21.0320, 105.8535, "32 Lò Sũ, Hoàn Kiếm", 4.6, 290, "romantic", "bar, view_ho", "16:00 - 24:00", 5, "$$$"),
            ("Cousins Tây Hồ", 21.0660, 105.8230, "7 Ngõ 58 Từ Hoa, Tây Hồ", 4.5, 340, "romantic", "restaurant, dinner, garden", "11:00 - 22:30", 4, "$$$"),
            ("El Gaucho Steakhouse", 21.0338, 105.8565, "11 Tràng Tiền, Hoàn Kiếm", 4.6, 1200, "romantic", "restaurant, dinner, luxury", "11:00 - 23:30", 8, "$$$"),
            ("Rhythm Restaurant", 21.0325, 105.8530, "78 Hàng Bạc, Hoàn Kiếm", 4.7, 310, "romantic", "restaurant, dinner, view_ho", "11:30 - 22:30", 3, "$$$"),
            ("Dalcheeni Indian Dining", 21.0635, 105.8282, "100 Xuân Diệu, Tây Hồ", 4.5, 420, "romantic", "restaurant, dinner, lakeside", "11:00 - 22:30", 4, "$$$"),
            ("Bánh mì Bistro Tràng Tiền", 21.0260, 105.8545, "5 Tràng Tiền, Hoàn Kiếm", 4.4, 280, "romantic", "cafe, french_vibe", "08:00 - 22:00", 5, "$$"),
            ("C'est Si Bon Cafe", 21.0248, 105.8170, "18 Nguyên Hồng, Đống Đa", 4.5, 540, "romantic", "cafe, sweet, modern", "09:00 - 22:30", 6, "$$"),
            ("De.Tầm Cafe", 21.0220, 105.8450, "33 Yên Thế, Ba Đình", 4.6, 290, "romantic", "cafe, hidden, garden", "08:00 - 22:30", 3, "$$"),
            ("Eden Coffee Cathedral", 21.0285, 105.8488, "2 Nhà Thờ, Hoàn Kiếm", 4.4, 1150, "romantic", "cafe, view_cathedral, rooftop", "08:00 - 23:00", 11, "$$"),

            # Extra Active (10 items to reach 30 active)
            ("Tiệm Boardgame Meeple", 21.0125, 105.8485, "15 Ngõ Đỗ Thuận, Hai Bà Trưng", 4.5, 140, "active", "cafe, boardgame", "09:00 - 22:30", 8, "$"),
            ("Xưởng Tranh Lộc Art", 21.0425, 105.7850, "Ngõ 180 Trần Duy Hưng, Cầu Giấy", 4.7, 65, "active", "workshop, painting", "09:00 - 18:00", 2, "$$$"),
            ("Bảo tàng Lịch sử Quân sự", 21.0322, 105.8390, "28A Điện Biên Phủ, Ba Đình", 4.5, 1950, "active", "museum, historical, photo", "08:00 - 16:30", 6, "$"),
            ("Công viên Yên Sở", 20.9705, 105.8560, "Pháp Vân, Hoàng Mai", 4.4, 5600, "active", "park, stroll, picnic", "06:00 - 19:00", 18, "$"),
            ("VR World Ba Đình", 21.0350, 105.8280, "88 Đốc Ngữ, Ba Đình", 4.4, 180, "active", "gaming, tech", "09:00 - 22:00", 5, "$$"),
            ("Bắn Cung CLB Ha Noi", 21.0410, 105.8080, "Xuân La, Tây Hồ", 4.3, 110, "active", "sports, archery", "08:30 - 21:30", 4, "$$"),
            ("Leo Núi VietClimb Tây Hồ", 21.0580, 105.8180, "76 An Dương, Tây Hồ", 4.5, 190, "active", "sports, fitness", "09:00 - 22:00", 3, "$$"),
            ("Chợ đêm Đồng Xuân", 21.0375, 105.8495, "Phố Đồng Xuân, Hoàn Kiếm", 4.3, 12500, "active", "stroll, shopping, street_food", "18:00 - 23:30 (Thứ 6-CN)", 35, "$"),
            ("Tổ hợp Complex Láng Hạ", 21.0175, 105.8125, "12 Ngõ 84 Láng Hạ, Đống Đa", 4.5, 230, "active", "complex, photogenic", "08:00 - 22:00", 12, "$$"),
            ("Lớp học cắm hoa đôi Florist", 21.0290, 105.8420, "45 Nguyễn Trường Tộ, Ba Đình", 4.8, 48, "active", "workshop, flowers", "09:00 - 17:30", 2, "$$$"),

            # Extra Food (10 items to reach 30 food)
            ("Phở gà Nguyệt Phủ Doãn", 21.0305, 105.8472, "5b Phủ Doãn, Hoàn Kiếm", 4.4, 1950, "food", "local_food, chicken_pho, night", "17:00 - 06:00", 18, "$$"),
            ("Phở bò Tư Lùn Hàng Mã", 21.0372, 105.8485, "68 Hàng Mã, Hoàn Kiếm", 4.3, 850, "food", "local_food, breakfast", "06:00 - 13:00", 14, "$"),
            ("Bánh mì 25 Hàng Cá", 21.0362, 105.8505, "25 Hàng Cá, Hoàn Kiếm", 4.6, 5200, "food", "local_food, budget", "07:00 - 21:00", 16, "$"),
            ("Cháo sườn sụn Huyền Anh chợ Đồng Xuân", 21.0378, 105.8492, "14 Đồng Xuân, Hoàn Kiếm", 4.2, 3400, "food", "local_food, street_food, night", "18:00 - 02:00", 25, "$"),
            ("Nướng ngói gầm cầu Hoàn Kiếm", 21.0375, 105.8475, "Phố Gầm Cầu, Hoàn Kiếm", 4.1, 2800, "food", "local_food, grill, night", "17:00 - 24:00", 22, "$$"),
            ("Quán Ốc Tống Duy Tân", 21.0308, 105.8440, "5 Tống Duy Tân, Hoàn Kiếm", 4.3, 1150, "food", "local_food, street_food, night", "15:00 - 02:00", 20, "$$"),
            ("Bún chả Cửa Đông", 21.0335, 105.8465, "21 Đường Thành, Hoàn Kiếm", 4.4, 1850, "food", "local_food, lunch", "10:30 - 20:00", 18, "$$"),
            ("Xôi xéo cô Mây Hàng Bài", 21.0228, 105.8532, "35 Hàng Bài, Hoàn Kiếm", 4.5, 1200, "food", "local_food, breakfast", "06:00 - 09:30", 24, "$"),
            ("Chè xoài Nguyễn Trường Tộ", 21.0415, 105.8432, "2 Ngõ Trạm, Hoàn Kiếm", 4.3, 790, "food", "sweet, street_food", "11:00 - 22:30", 14, "$"),
            ("Nem chua rán ngõ Tạm Thương", 21.0322, 105.8478, "Ngõ Tạm Thương, Hoàn Kiếm", 4.3, 2400, "food", "street_food, classic", "12:00 - 23:00", 26, "$")
        ]
        
        # Insert main seed
        for name, lat, lon, addr, rat, revs, vibe, tags, hrs, crwd, price, desc in seed_data:
            cursor.execute("""
            INSERT INTO spots (name, latitude, longitude, address, rating, review_count, vibe, tags, open_hours, crowd_level, price_range, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, lat, lon, addr, rat, revs, vibe, tags, hrs, crwd, price, desc))
            
        # Insert extra programmatics to reach exactly 80 total
        for item in extras:
            if len(item) == 12:
                name, lat, lon, addr, rat, revs, vibe, tags, hrs, crwd, price, desc = item
            else: # size 11, default description
                name, lat, lon, addr, rat, revs, vibe, tags, hrs, crwd, price = item
                desc = f"Địa điểm tuyệt vời dành cho các cặp đôi trải nghiệm vibe {vibe} tại Hà Nội với không gian sạch sẽ, phong cách nhiệt tình."
            
            cursor.execute("""
            INSERT INTO spots (name, latitude, longitude, address, rating, review_count, vibe, tags, open_hours, crowd_level, price_range, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, lat, lon, addr, rat, revs, vibe, tags, hrs, crwd, price, desc))
            
    conn.commit()
    conn.close()
    print("Database initialized and seeded with 80 Hanoi spots.")

def get_spots_by_vibe(vibe):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spots WHERE vibe = ?", (vibe,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_spot_by_id(spot_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spots WHERE id = ?", (spot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_all_spots():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spots")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def log_event(event_type, spot_id, old_time_slot, new_time_slot, reason, vibe, num_people):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO event_logs (event_type, spot_id, old_time_slot, new_time_slot, reason, vibe, num_people)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event_type, spot_id, old_time_slot, new_time_slot, reason, vibe, num_people))
    conn.commit()
    conn.close()

def save_search_result(place_data: dict):
    """Lưu kết quả search từ Google Maps vào database với ảnh."""
    conn = get_db_connection()
    cursor = conn.cursor()

    images_json = json.dumps(place_data.get("images", []))

    cursor.execute("""
    INSERT INTO spots (name, latitude, longitude, address, rating, review_count,
                       vibe, tags, open_hours, crowd_level, price_range, description, images, data_id)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        place_data.get("title"),
        place_data.get("latitude", 0),
        place_data.get("longitude", 0),
        place_data.get("address", ""),
        place_data.get("rating", 0),
        place_data.get("reviews", 0),
        "search_result",  # vibe
        place_data.get("type", ""),  # tags
        place_data.get("open_state", ""),  # open_hours
        0,  # crowd_level
        place_data.get("price", ""),  # price_range
        f"{place_data.get('title')} - Từ Google Maps",  # description
        images_json,
        place_data.get("data_id", "")
    ))

    spot_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return spot_id

def get_spot_images(spot_id):
    """Lấy danh sách ảnh của một spot."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT images FROM spots WHERE id = ?", (spot_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            return json.loads(row[0])
        except (json.JSONDecodeError, TypeError):
            return []
    return []

if __name__ == "__main__":
    init_db()
