# Generated by Django 2.2 on 2019-12-20 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FuturesInstrument',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='상품명')),
                ('symbol', models.CharField(max_length=16, verbose_name='상품코드')),
                ('currency', models.CharField(choices=[('USD', 'Dollar'), ('EUR', 'EURO'), ('HKD', 'Hongkong Dollar')], default='USD', max_length=16, verbose_name='거래 통화')),
                ('exchange', models.CharField(choices=[('CME', 'CME'), ('NYMEX', 'NYMEX'), ('CBOT', 'CBOT'), ('EUREX', 'EUREX'), ('HKEX', 'HKEX'), ('SGX', 'SGX'), ('ICE_US', 'ICE_US')], max_length=16, verbose_name='거래소')),
                ('market', models.CharField(choices=[('CUR', '통화'), ('IDX', '지수'), ('INT', '금리'), ('ENG', '에너지'), ('MTL', '금속'), ('Grain', '곡물'), ('Tropical', '열대과일'), ('Meat', '육류')], max_length=16, verbose_name='시장 구분')),
                ('tickunit', models.DecimalField(decimal_places=6, max_digits=12, verbose_name='호가 단위')),
                ('tickprice', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='호가당 가격')),
                ('margin', models.DecimalField(decimal_places=0, max_digits=5, verbose_name='증거금')),
                ('decimal_places', models.SmallIntegerField(verbose_name='소수점 자리수')),
                ('opentime', models.TimeField(verbose_name='거래 시작시간')),
                ('closetime', models.TimeField(verbose_name='거래 종료시간')),
                ('has_history', models.BooleanField(verbose_name='과거데이터 유무')),
                ('is_tradable', models.BooleanField(verbose_name='거래가능여부')),
            ],
        ),
    ]