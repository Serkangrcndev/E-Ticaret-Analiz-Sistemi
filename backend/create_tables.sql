-- Site Güvenlik Analizi Veritabanı Tabloları
-- SQL Server için tablo oluşturma scripti

-- Önce veritabanını oluştur (eğer yoksa)
IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = 'SiteGuvenlikDB')
BEGIN
    CREATE DATABASE [SiteGuvenlikDB];
    PRINT 'SiteGuvenlikDB veritabanı oluşturuldu.';
END
ELSE
BEGIN
    PRINT 'SiteGuvenlikDB veritabanı zaten mevcut.';
END
GO

USE [SiteGuvenlikDB]
GO

-- 1. Sites Tablosu (Ana Site Bilgileri)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Sites]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Sites] (
        [SiteID] INT PRIMARY KEY IDENTITY(1,1),
        [Domain] NVARCHAR(255) UNIQUE NOT NULL,
        [SiteName] NVARCHAR(255),
        [CreatedDate] DATETIME DEFAULT GETDATE(),
        [LastScannedDate] DATETIME,
        [RiskScore] INT DEFAULT 0,
        [Status] NVARCHAR(50) DEFAULT 'Active',
        [Description] NVARCHAR(MAX),
        [Category] NVARCHAR(100)
    )
    PRINT 'Sites tablosu oluşturuldu.'
END
ELSE
BEGIN
    PRINT 'Sites tablosu zaten mevcut.'
END
GO

-- 2. Complaints Tablosu (Şikayet/Yorum Kayıtları)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[Complaints]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[Complaints] (
        [ComplaintID] INT PRIMARY KEY IDENTITY(1,1),
        [SiteID] INT NOT NULL,
        [Source] NVARCHAR(100) NOT NULL, -- 'sikayetvar', 'google', 'twitter', 'reddit', 'eksisozluk', 'trustpilot', 'instagram', 'facebook'
        [Title] NVARCHAR(500),
        [Content] NVARCHAR(MAX),
        [Author] NVARCHAR(255),
        [Date] DATETIME,
        [Rating] INT, -- 1-5 arası
        [Sentiment] NVARCHAR(50), -- 'positive', 'negative', 'neutral'
        [URL] NVARCHAR(1000),
        [ScrapedDate] DATETIME DEFAULT GETDATE(),
        FOREIGN KEY ([SiteID]) REFERENCES [dbo].[Sites]([SiteID]) ON DELETE CASCADE
    )
    
    -- Index'ler
    CREATE INDEX IX_Complaints_SiteID ON [dbo].[Complaints]([SiteID])
    CREATE INDEX IX_Complaints_Source ON [dbo].[Complaints]([Source])
    CREATE INDEX IX_Complaints_Sentiment ON [dbo].[Complaints]([Sentiment])
    CREATE INDEX IX_Complaints_Date ON [dbo].[Complaints]([Date])
    
    PRINT 'Complaints tablosu oluşturuldu.'
END
ELSE
BEGIN
    PRINT 'Complaints tablosu zaten mevcut.'
END
GO

-- 3. RiskAnalysis Tablosu (Risk Analizi Sonuçları)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[RiskAnalysis]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[RiskAnalysis] (
        [AnalysisID] INT PRIMARY KEY IDENTITY(1,1),
        [SiteID] INT NOT NULL,
        [TotalComplaints] INT DEFAULT 0,
        [NegativeSentimentCount] INT DEFAULT 0,
        [PositiveSentimentCount] INT DEFAULT 0,
        [NeutralSentimentCount] INT DEFAULT 0,
        [AverageRating] DECIMAL(3,2),
        [RiskLevel] NVARCHAR(50), -- 'Low', 'Medium', 'High', 'Critical'
        [AnalysisDate] DATETIME DEFAULT GETDATE(),
        [Details] NVARCHAR(MAX), -- JSON formatında detaylar
        FOREIGN KEY ([SiteID]) REFERENCES [dbo].[Sites]([SiteID]) ON DELETE CASCADE
    )
    
    CREATE INDEX IX_RiskAnalysis_SiteID ON [dbo].[RiskAnalysis]([SiteID])
    CREATE INDEX IX_RiskAnalysis_RiskLevel ON [dbo].[RiskAnalysis]([RiskLevel])
    
    PRINT 'RiskAnalysis tablosu oluşturuldu.'
END
ELSE
BEGIN
    PRINT 'RiskAnalysis tablosu zaten mevcut.'
END
GO

-- 4. ScrapingHistory Tablosu (Scraping Geçmişi)
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ScrapingHistory]') AND type in (N'U'))
BEGIN
    CREATE TABLE [dbo].[ScrapingHistory] (
        [HistoryID] INT PRIMARY KEY IDENTITY(1,1),
        [SiteID] INT NOT NULL,
        [Source] NVARCHAR(100) NOT NULL,
        [Status] NVARCHAR(50), -- 'Success', 'Failed', 'Partial'
        [RecordsFound] INT DEFAULT 0,
        [ErrorMessage] NVARCHAR(MAX),
        [ScrapedDate] DATETIME DEFAULT GETDATE(),
        [Duration] INT, -- Saniye cinsinden süre
        FOREIGN KEY ([SiteID]) REFERENCES [dbo].[Sites]([SiteID]) ON DELETE CASCADE
    )
    
    CREATE INDEX IX_ScrapingHistory_SiteID ON [dbo].[ScrapingHistory]([SiteID])
    CREATE INDEX IX_ScrapingHistory_Source ON [dbo].[ScrapingHistory]([Source])
    CREATE INDEX IX_ScrapingHistory_Status ON [dbo].[ScrapingHistory]([Status])
    CREATE INDEX IX_ScrapingHistory_ScrapedDate ON [dbo].[ScrapingHistory]([ScrapedDate])
    
    PRINT 'ScrapingHistory tablosu oluşturuldu.'
END
ELSE
BEGIN
    PRINT 'ScrapingHistory tablosu zaten mevcut.'
END
GO

-- 5. Örnek Veri Ekleme (Opsiyonel)
-- Test için örnek site ekle
IF NOT EXISTS (SELECT * FROM [dbo].[Sites] WHERE Domain = 'example.com')
BEGIN
    INSERT INTO [dbo].[Sites] (Domain, SiteName, Description, Category)
    VALUES ('example.com', 'Example Site', 'Test sitesi', 'E-ticaret')
    
    DECLARE @SiteID INT = SCOPE_IDENTITY()
    
    -- Örnek şikayetler
    INSERT INTO [dbo].[Complaints] (SiteID, Source, Title, Content, Author, Date, Rating, Sentiment, URL)
    VALUES 
        (@SiteID, 'sikayetvar', 'Ürün gelmedi', 'Sipariş verdim ama ürün gelmedi. Para iade istiyorum.', 'Kullanıcı1', GETDATE() - 5, 1, 'negative', 'https://sikayetvar.com/example'),
        (@SiteID, 'google', 'Güvenilir site', 'Çok memnun kaldım, hızlı teslimat.', 'Kullanıcı2', GETDATE() - 3, 5, 'positive', 'https://google.com/search'),
        (@SiteID, 'reddit', 'Kötü hizmet', 'Müşteri hizmetleri çok kötü, cevap vermiyorlar.', 'RedditUser', GETDATE() - 2, 2, 'negative', 'https://reddit.com/r/complaints')
    
    -- Risk analizi
    INSERT INTO [dbo].[RiskAnalysis] (SiteID, TotalComplaints, NegativeSentimentCount, PositiveSentimentCount, NeutralSentimentCount, AverageRating, RiskLevel)
    VALUES (@SiteID, 3, 2, 1, 0, 2.67, 'High')
    
    PRINT 'Örnek veri eklendi.'
END
ELSE
BEGIN
    PRINT 'Örnek veri zaten mevcut.'
END
GO

PRINT 'Tüm tablolar başarıyla oluşturuldu!'
GO

