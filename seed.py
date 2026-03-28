"""
Demo ma'lumotlar qo'shish uchun skript
Run: python seed.py
"""
import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models import User, News, UserRole, UserStatus
from app.auth import hash_password, slugify

DEMO_NEWS = [
    {
        "title": "O'zbekistonda sun'iy intellekt texnologiyalari jadal rivojlanmoqda",
        "summary": "Mamlakat bo'ylab yuzlab startaplar AI sohasida faoliyat yuritmoqda, hukumat esa texnologiya sohasiga investitsiyalarni oshirmoqda.",
        "content": """O'zbekiston texnologiya sohasi so'nggi yillarda sezilarli o'sishni boshdan kechirmoqda. Ayniqsa, sun'iy intellekt (AI) va machine learning texnologiyalari bo'yicha mahalliy mutaxassislar soni yildan-yilga ko'payib bormoqda.

Toshkent shahridagi texnopark hududida 200 dan ortiq IT kompaniyalar faoliyat yuritib, ularning aksariyati AI asosidagi mahsulotlar yaratmoqda. Hukumat bu soha rivojlanishi uchun maxsus grantlar va soliq imtiyozlari belgilab qo'ygan.

Raqamli O'zbekiston 2030 dasturi doirasida mamlakatning barcha ta'lim muassasalarida dasturlash va AI fanlarini o'qitish boshlangan. Bu tashabbuslar kelgusida O'zbekistonni mintaqaning texnologiya markaziga aylantirishi kutilmoqda.

Xalqaro ekspertlarning fikricha, O'zbekiston to'g'ri strategiyani tanlab, 5-7 yil ichida IT eksporti bo'yicha Markaziy Osiyo yetakchisiga aylanishi mumkin.""",
        "category": "Texnologiya",
        "image_url": "https://images.unsplash.com/photo-1677442135703-1787eea5ce01?w=800&h=450&fit=crop"
    },
    {
        "title": "O'zbekiston terma jamoasi jahon chempionatiga yo'l oldi",
        "summary": "Milliy futbol terma jamoa tarixiy g'alabani qo'lga kiritdi va birinchi marta jahon chempionati saralash bosqichiga chiqdi.",
        "content": """O'zbekiston milliy futbol terma jamoasi kecha Toshkentda bo'lib o'tgan hal qiluvchi o'yinda raqibini mag'lubiyatga uchratib, tarixiy yutuqqa erishdi.

Uchrashuv juda keskin kechdi. Birinchi yarim vaqtda 0:0 hisobida tugagan o'yinda ikkinchi davrda terma jamoamiz 2 ta gol urdi. Jamoaning asosiy hujumchisi mahoratli zarbalar bilan g'alabaga hissa qo'shdi.

Bu g'alaba milliy jamoa tarixidagi eng muhim natijalardan biri hisoblanadi. Jamoaning bosh murabbiyi matbuot anjumanida: "Futbolchilar bugun qalb bilan o'ynashdi, bu g'alaba butun xalqimizga bag'ishlangan," dedi.

Keyingi bosqichda O'zbekiston kuchli raqiblar bilan o'ynaydi. Saralash o'yinlari kelasi yil boshlanadi.""",
        "category": "Sport",
        "image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800&h=450&fit=crop"
    },
    {
        "title": "O'zbekiston iqtisodiyoti 7% o'sdi — rasmiy ma'lumotlar",
        "summary": "Iqtisodiyot vazirligi ma'lumotlariga ko'ra, joriy yilda yalpi ichki mahsulot o'sishi kutilganidan ham yuqori bo'ldi.",
        "content": """O'zbekiston iqtisodiyoti joriy yil davomida 7.2 foizga o'sganini Iqtisodiyot va moliya vazirligi rasmiy ravishda e'lon qildi. Bu ko'rsatkich mintaqadagi eng yuqori o'sish sur'atlaridan biri hisoblanadi.

O'sishga asosiy hissa qo'shgan sohalar: sanoat ishlab chiqarish (+9.1%), xizmatlar sektori (+8.3%) va qishloq xo'jaligi (+5.7%). Eksport hajmi ham 15 foizga oshdi.

Xalqaro valyuta fondi va Jahon banki O'zbekistonning iqtisodiy islohotlar yo'lini ijobiy baholamoqda. Mamlakat investitsiya muhitini yaxshilash bo'yicha muhim qadamlar tashladi.

Ammo ekspertlar inflyatsiya va ishsizlik muammolari hali to'liq hal etilmaganiga e'tibor qaratmoqda. Hukumat bu sohalarda ham aniq chora-tadbirlar ishlab chiqmoqda.""",
        "category": "Iqtisodiyot",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=450&fit=crop"
    },
    {
        "title": "Toshkentda yangi metro liniyasi ochildi",
        "summary": "Poytaxtning yangi metro liniyasi rasman foydalanishga topshirildi. Har kuni 200 ming yo'lovchiga xizmat qilishi kutilmoqda.",
        "content": """Toshkent metropoliteni yangi liniyasining rasmiy ochilish marosimi bo'lib o'tdi. Prezident va shahar hokimi ishtirokida bo'lgan marosimda yangi stansiyalar taqdim etildi.

Yangi liniya shaharning sharqiy qismini markaziy tumanlar bilan bog'laydi. Umumiy uzunligi 18 km bo'lgan yo'nalishda 12 ta stansiya mavjud. Poyezdlar har 3 daqiqada harakat qiladi.

Metro vagonlari zamonaviy texnologiyalar bilan jihozlangan: konditsioner, Wi-Fi, elektron ma'lumot ekranlari va nogironlar uchun maxsus qurilmalar o'rnatilgan.

Toshkent shahri transport muammosini hal qilish bo'yicha kompleks dastur amalga oshirmoqda. Kelgusi 3 yil ichida yana 2 ta yangi liniya qurilishi rejalashtirilgan.""",
        "category": "Dunyo",
        "image_url": "https://images.unsplash.com/photo-1555661530-68c8e98db4f9?w=800&h=450&fit=crop"
    },
    {
        "title": "O'zbek kinosi xalqaro festivallarda tan olindi",
        "summary": "Yosh rejissyorlarimizning filmlari Berlin va Kann festivallarida yuqori baholandi.",
        "content": """O'zbekiston kino sanoati so'nggi yillarda misli ko'rilmagan rivojlanishni boshdan kechirmoqda. Yosh iste'dodli rejissyorlar yaratgan filmlar xalqaro miqyosda e'tirof etilmoqda.

Berlin xalqaro kino festivalida O'zbekiston rejissyorining filmi "Eng yaxshi debyu" nominatsiyasida sovrin oldi. Bu mamlakat kino tarixi uchun muhim yutuq hisoblanadi.

Madaniyat vazirligi ma'lumotlariga ko'ra, kino sanoatiga davlat tomonidan ajratiladigan mablag' 3 barobarga oshirildi. Toshkentda yangi zamonaviy kinostudiya qurilishi ham rejalashtirilgan.

O'zbek kinosi nafaqat mahalliy, balki xalqaro auditoriyani ham o'ziga jalb eta boshlamoqda. Yaqinda bir nechta film xorijiy streaming platformalarda namoyish etilishi ma'lum qilindi.""",
        "category": "Madaniyat",
        "image_url": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&h=450&fit=crop"
    },
    {
        "title": "Dunyo bo'ylab iqlim o'zgarishi muammosi keskinlashmoqda",
        "summary": "BMT iqlim bo'yicha yangi hisobotni e'lon qildi. Mutaxassislar tezkor choralar ko'rish zarurligini ta'kidlamoqda.",
        "content": """BMT ning iqlim bo'yicha maxsus komissiyasi yangi hisobot e'lon qilib, global isish muammosi kutilganidan tezroq rivojlanayotganini xabar qildi.

Hisobotga ko'ra, Yer sirtining o'rtacha harorati so'nggi 10 yilda 0.3 daraja ko'tarildi. Bu qutb muzliklarining erishiga va dengiz sathining ko'tarilishiga sabab bo'lmoqda.

O'rta Osiyo mamlakatlari, jumladan O'zbekiston, iqlim o'zgarishidan ko'proq zarar ko'rishi mumkin. Amudaryo va Sirdaryo daryolaridagi suv hajmi kamayib bormoqda, bu esa qishloq xo'jaligiga katta xavf tug'dirmoqda.

Ekspertlar barcha davlatlardan zudlik bilan karbon chiqindilarini kamaytirish va qayta tiklanuvchi energiyaga o'tishni talab qilmoqda. Keyingi yili bo'ladigan iqlim sammitida yangi kelishuvlar imzolanishi kutilmoqda.""",
        "category": "Dunyo",
        "image_url": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&h=450&fit=crop"
    },
]

async def seed():
    await init_db()
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Get admin user
        result = await db.execute(select(User).where(User.email == "admin@news.uz"))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                full_name="Super Admin",
                email="admin@news.uz",
                hashed_password=hash_password("admin123"),
                role=UserRole.admin,
                status=UserStatus.approved
            )
            db.add(admin)
            await db.flush()
            print("✅ Admin yaratildi")

        # Add demo news
        for i, item in enumerate(DEMO_NEWS):
            base_slug = slugify(item["title"])
            existing = (await db.execute(select(News).where(News.slug == base_slug))).scalar_one_or_none()
            if not existing:
                news = News(
                    title=item["title"],
                    slug=base_slug,
                    summary=item["summary"],
                    content=item["content"],
                    category=item["category"],
                    image_url=item["image_url"],
                    author_id=admin.id,
                    is_published=True,
                    views=10 * (i + 1)
                )
                db.add(news)
                print(f"✅ Yangilik qo'shildi: {item['title'][:50]}...")

        # Add demo pending user
        demo_result = await db.execute(select(User).where(User.email == "user@test.uz"))
        demo_user = demo_result.scalar_one_or_none()
        if not demo_user:
            demo_user = User(
                full_name="Demo Foydalanuvchi",
                email="user@test.uz",
                hashed_password=hash_password("user123"),
                role=UserRole.user,
                status=UserStatus.pending
            )
            db.add(demo_user)
            print("✅ Demo foydalanuvchi qo'shildi (kutayotgan holat)")

        await db.commit()
        print("\n🎉 Seed muvaffaqiyatli yakunlandi!")
        print("="*50)
        print("Admin login: admin@news.uz | admin123")
        print("Demo user: user@test.uz | user123 (pending)")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(seed())
