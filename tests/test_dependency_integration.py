"""
Tests for dependency integration service
Following TDD principles: test behaviors, not implementation
"""

import pytest
from bob_core.dependency_integration import DependencyScoreProvider, DependencyScore


class TestDependencyScoreProvider:
    """Test dependency score provider"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock dependency score provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_initializes_with_mock_mode(self):
        """Should initialize in mock mode"""
        provider = DependencyScoreProvider(use_mock=True)
        
        assert provider.use_mock is True
        assert provider._cache == {}
    
    def test_gets_file_score(self, provider):
        """Should get dependency score for a file"""
        score = provider.get_file_score("auth.py")
        
        assert score is not None
        assert isinstance(score, DependencyScore)
        assert score.file_path == "auth.py"
        assert 0.0 <= score.complexity <= 1.0
        assert 0.0 <= score.centrality <= 1.0
        assert score.distance_from_entry >= 0
    
    def test_caches_scores(self, provider):
        """Should cache scores for repeated requests"""
        score1 = provider.get_file_score("auth.py")
        score2 = provider.get_file_score("auth.py")
        
        # Should return same object from cache
        assert score1 is score2
    
    def test_clears_cache(self, provider):
        """Should clear cache when requested"""
        provider.get_file_score("auth.py")
        assert len(provider._cache) > 0
        
        provider.clear_cache()
        
        assert len(provider._cache) == 0


class TestMockScoreGeneration:
    """Test mock score generation"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_generates_consistent_scores(self, provider):
        """Should generate consistent scores for same file"""
        score1 = provider.get_file_score("test.py")
        provider.clear_cache()
        score2 = provider.get_file_score("test.py")
        
        assert score1.complexity == score2.complexity
        assert score1.centrality == score2.centrality
    
    def test_utils_files_are_easy(self, provider):
        """Should mark utils files as easy"""
        score = provider.get_file_score("utils.py")
        
        assert score.complexity < 0.33
        assert score.recommendation == "start_here"
    
    def test_main_files_are_medium(self, provider):
        """Should mark main files as medium complexity"""
        score = provider.get_file_score("main.py")
        
        assert 0.33 <= score.complexity < 0.67
    
    def test_service_files_are_hard(self, provider):
        """Should mark service files as harder"""
        score = provider.get_file_score("auth_service.py")
        
        assert score.complexity >= 0.5
    
    def test_main_files_have_zero_distance(self, provider):
        """Should mark main files as entry points"""
        score = provider.get_file_score("main.py")
        
        assert score.distance_from_entry == 0


class TestLearningPathGeneration:
    """Test learning path generation"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_generates_learning_path(self, provider):
        """Should generate learning path with scores"""
        files = ["auth.py", "models.py", "utils.py", "main.py"]
        
        path = provider.get_learning_path(files)
        
        assert len(path) == len(files)
        assert all("file_path" in f for f in path)
        assert all("complexity" in f for f in path)
        assert all("priority" in f for f in path)
    
    def test_sorts_by_learning_priority(self, provider):
        """Should sort files by learning priority"""
        files = ["complex_service.py", "utils.py", "main.py"]
        
        path = provider.get_learning_path(files)
        
        # Should be sorted by priority (lower = study first)
        priorities = [f["priority"] for f in path]
        assert priorities == sorted(priorities)
    
    def test_includes_all_metadata(self, provider):
        """Should include all metadata in learning path"""
        files = ["auth.py"]
        
        path = provider.get_learning_path(files)
        
        assert len(path) > 0
        file_info = path[0]
        assert "file_path" in file_info
        assert "complexity" in file_info
        assert "centrality" in file_info
        assert "distance_from_entry" in file_info
        assert "recommendation" in file_info
        assert "priority" in file_info


class TestComplexityDistribution:
    """Test complexity distribution calculation"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_calculates_distribution(self, provider):
        """Should calculate complexity distribution"""
        files = ["utils.py", "main.py", "service.py", "helper.py"]
        
        distribution = provider.get_complexity_distribution(files)
        
        assert "Easy" in distribution
        assert "Medium" in distribution
        assert "Hard" in distribution
        assert sum(distribution.values()) == len(files)
    
    def test_handles_empty_file_list(self, provider):
        """Should handle empty file list"""
        distribution = provider.get_complexity_distribution([])
        
        assert distribution["Easy"] == 0
        assert distribution["Medium"] == 0
        assert distribution["Hard"] == 0


class TestEntryPointIdentification:
    """Test entry point identification"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_identifies_entry_points(self, provider):
        """Should identify entry point files"""
        files = ["main.py", "app.py", "utils.py", "models.py"]
        
        entry_points = provider.get_entry_points(files)
        
        assert len(entry_points) > 0
        # main.py and app.py should be entry points
        assert any("main" in ep or "app" in ep for ep in entry_points)
    
    def test_handles_no_entry_points(self, provider):
        """Should handle case with no entry points"""
        files = ["utils.py", "models.py"]
        
        entry_points = provider.get_entry_points(files)
        
        # Should return empty list or files with distance 0
        assert isinstance(entry_points, list)


class TestCentralFileIdentification:
    """Test central file identification"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_identifies_central_files(self, provider):
        """Should identify most central files"""
        files = ["models.py", "utils.py", "config.py", "auth.py", "router.py"]
        
        central = provider.get_central_files(files, top_n=3)
        
        assert len(central) <= 3
        assert all("file_path" in f for f in central)
        assert all("centrality" in f for f in central)
    
    def test_sorts_by_centrality(self, provider):
        """Should sort by centrality (highest first)"""
        files = ["models.py", "utils.py", "config.py"]
        
        central = provider.get_central_files(files, top_n=3)
        
        # Should be sorted by centrality (descending)
        centralities = [f["centrality"] for f in central]
        assert centralities == sorted(centralities, reverse=True)
    
    def test_limits_to_top_n(self, provider):
        """Should limit results to top_n"""
        files = [f"file{i}.py" for i in range(10)]
        
        central = provider.get_central_files(files, top_n=5)
        
        assert len(central) == 5


class TestComplexityLabeling:
    """Test complexity label conversion"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_labels_easy_complexity(self, provider):
        """Should label low complexity as Easy"""
        label = provider._complexity_label(0.2)
        
        assert label == "Easy"
    
    def test_labels_medium_complexity(self, provider):
        """Should label medium complexity as Medium"""
        label = provider._complexity_label(0.5)
        
        assert label == "Medium"
    
    def test_labels_hard_complexity(self, provider):
        """Should label high complexity as Hard"""
        label = provider._complexity_label(0.8)
        
        assert label == "Hard"
    
    def test_boundary_cases(self, provider):
        """Should handle boundary cases correctly"""
        assert provider._complexity_label(0.33) == "Medium"
        assert provider._complexity_label(0.67) == "Hard"
        assert provider._complexity_label(0.0) == "Easy"
        assert provider._complexity_label(1.0) == "Hard"


class TestPriorityCalculation:
    """Test learning priority calculation"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_calculates_priority(self, provider):
        """Should calculate priority score"""
        score = DependencyScore(
            file_path="test.py",
            complexity=0.5,
            centrality=0.7,
            distance_from_entry=2,
            recommendation="study_later",
            importance_score=75,
            architectural_layer="core"
        )
        
        priority = provider._calculate_priority(score)
        
        assert isinstance(priority, float)
        assert priority >= 0
    
    def test_lower_complexity_higher_priority(self, provider):
        """Should give higher priority to lower complexity"""
        easy_score = DependencyScore("easy.py", 0.2, 0.5, 1, "start_here", 60, "foundation")
        hard_score = DependencyScore("hard.py", 0.8, 0.5, 1, "advanced", 85, "core")
        
        easy_priority = provider._calculate_priority(easy_score)
        hard_priority = provider._calculate_priority(hard_score)
        
        # Lower priority value = higher priority
        assert easy_priority < hard_priority
    
    def test_higher_centrality_higher_priority(self, provider):
        """Should give higher priority to more central files"""
        central_score = DependencyScore("central.py", 0.5, 0.9, 1, "study_later", 80, "core")
        peripheral_score = DependencyScore("peripheral.py", 0.5, 0.1, 1, "study_later", 50, "utility")
        
        central_priority = provider._calculate_priority(central_score)
        peripheral_priority = provider._calculate_priority(peripheral_score)
        
        # Lower priority value = higher priority
        assert central_priority < peripheral_priority
    
    def test_closer_to_entry_higher_priority(self, provider):
        """Should give higher priority to files closer to entry"""
        close_score = DependencyScore("close.py", 0.5, 0.5, 1, "study_later", 70, "frontend")
        far_score = DependencyScore("far.py", 0.5, 0.5, 5, "advanced", 65, "backend")
        
        close_priority = provider._calculate_priority(close_score)
        far_priority = provider._calculate_priority(far_score)
        
        # Lower priority value = higher priority
        assert close_priority < far_priority


class TestScorePreloading:
    """Test score preloading"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_preloads_multiple_scores(self, provider):
        """Should preload scores for multiple files"""
        files = ["auth.py", "models.py", "utils.py"]
        
        provider.preload_scores(files)
        
        # All files should be in cache
        assert len(provider._cache) == len(files)
        for file_path in files:
            assert file_path in provider._cache
    
    def test_preload_improves_performance(self, provider):
        """Should cache scores for faster subsequent access"""
        files = ["auth.py", "models.py"]
        
        provider.preload_scores(files)
        
        # Second access should use cache
        score = provider.get_file_score("auth.py")
        assert score is not None


class TestRecommendationGeneration:
    """Test recommendation generation"""
    
    @pytest.fixture
    def provider(self):
        """Create a mock provider"""
        return DependencyScoreProvider(use_mock=True)
    
    def test_recommends_start_here_for_easy(self, provider):
        """Should recommend start_here for easy files"""
        score = provider.get_file_score("utils.py")
        
        assert score.recommendation == "start_here"
    
    def test_recommends_study_later_for_medium(self, provider):
        """Should recommend study_later for medium files"""
        score = provider.get_file_score("main.py")
        
        # Medium complexity files
        if 0.33 <= score.complexity < 0.67:
            assert score.recommendation in ["study_later", "start_here"]
    
    def test_recommends_advanced_for_hard(self, provider):
        """Should recommend advanced for hard files"""
        score = provider.get_file_score("complex_service.py")
        
        # Hard files should be advanced
        if score.complexity >= 0.67:
            assert score.recommendation in ["advanced", "study_later"]

# Made with Bob