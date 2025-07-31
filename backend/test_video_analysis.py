#!/usr/bin/env python3
"""
Test pentru funcționalitatea de analiză video
"""

import cv2
import numpy as np
import os
import tempfile
from video_analyzer import VideoAnalyzer

def create_test_video(filename: str, duration_seconds: int = 5, fps: int = 30, add_artifacts: bool = False):
    """Creează un video de test pentru analiză"""
    
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    width, height = 640, 480
    
    out = cv2.VideoWriter(filename, fourcc, fps, (width, height))
    
    total_frames = duration_seconds * fps
    
    for i in range(total_frames):
        # Creează un frame cu gradient de culoare
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient care se schimbă în timp
        color_shift = (i * 255) // total_frames
        frame[:, :, 0] = color_shift  # Roșu
        frame[:, :, 1] = (255 - color_shift) // 2  # Verde
        frame[:, :, 2] = 255 - color_shift  # Albastru
        
        # Adaugă text cu numărul frame-ului
        cv2.putText(frame, f"Frame {i+1}/{total_frames}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        if add_artifacts:
            # Adaugă zgomot pentru a simula artefacte
            noise = np.random.normal(0, 25, frame.shape).astype(np.uint8)
            frame = cv2.add(frame, noise)
            
            # Adaugă blocuri JPEG simulate (doar la fiecare 8 pixeli)
            if i % 10 == 0:  # La fiecare 10 frame-uri
                for y in range(0, height, 8):
                    for x in range(0, width, 8):
                        # Simulează compresia prin reducerea detaliilor în blocuri 8x8
                        block = frame[y:y+8, x:x+8]
                        block_avg = np.mean(block, axis=(0, 1)).astype(np.uint8)
                        frame[y:y+8, x:x+8] = block_avg
        
        out.write(frame)
    
    out.release()
    print(f"Video de test creat: {filename}")

def test_video_analyzer():
    """Testează analizorul de video"""
    
    print("🎬 TESTEZ ANALIZORUL DE VIDEO")
    print("=" * 60)
    
    # Creează director temporar
    temp_dir = tempfile.mkdtemp()
    
    # Creează videoclipuri de test
    normal_video = os.path.join(temp_dir, "normal_video.mp4")
    corrupted_video = os.path.join(temp_dir, "corrupted_video.mp4")
    
    print("📹 Creez videoclipuri de test...")
    create_test_video(normal_video, duration_seconds=3, add_artifacts=False)
    create_test_video(corrupted_video, duration_seconds=3, add_artifacts=True)
    
    # Inițializează analizorul
    analyzer = VideoAnalyzer()
    
    # Test 1: Video normal
    print("\n🧪 TESTEZ VIDEO NORMAL")
    print("-" * 40)
    
    try:
        result_normal = analyzer.analyze_video_integrity(normal_video)
        
        print(f"✅ Analiză completă în {result_normal.get('processing_time_seconds', 0):.2f} secunde")
        print(f"📊 Verdict final: {result_normal.get('final_verdict', {}).get('verdict', 'N/A')}")
        print(f"🎯 Nivel risc: {result_normal.get('final_verdict', {}).get('risk_level', 'N/A')}")
        print(f"⚠️  Avertismente: {len(result_normal.get('final_verdict', {}).get('warnings', []))}")
        
        # Afișează detalii despre analize
        compression = result_normal.get('compression_analysis', {})
        temporal = result_normal.get('temporal_analysis', {})
        deepfake = result_normal.get('deepfake_analysis', {})
        
        print(f"\n📈 Analiză compresie:")
        print(f"   - Calitate: {compression.get('quality_level', 'N/A')}")
        print(f"   - Suspiciune modificări: {compression.get('modification_suspicion', 'N/A')}")
        
        print(f"\n⏱️  Analiză temporală:")
        print(f"   - Verdict: {temporal.get('temporal_verdict', 'N/A')}")
        print(f"   - Suspiciune editare: {temporal.get('edit_suspicion', 'N/A')}")
        
        print(f"\n👤 Analiză deepfake:")
        print(f"   - Fețe detectate: {deepfake.get('total_faces_detected', 0)}")
        print(f"   - Verdict: {deepfake.get('deepfake_verdict', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Eroare la analiza video normal: {e}")
    
    # Test 2: Video cu artefacte
    print("\n🧪 TESTEZ VIDEO CU ARTEFACTE")
    print("-" * 40)
    
    try:
        result_corrupted = analyzer.analyze_video_integrity(corrupted_video)
        
        print(f"✅ Analiză completă în {result_corrupted.get('processing_time_seconds', 0):.2f} secunde")
        print(f"📊 Verdict final: {result_corrupted.get('final_verdict', {}).get('verdict', 'N/A')}")
        print(f"🎯 Nivel risc: {result_corrupted.get('final_verdict', {}).get('risk_level', 'N/A')}")
        
        warnings = result_corrupted.get('final_verdict', {}).get('warnings', [])
        print(f"⚠️  Avertismente ({len(warnings)}):")
        for warning in warnings:
            print(f"   - {warning}")
        
        # Compară scorurile
        print(f"\n📊 COMPARAȚIE SCORURI:")
        normal_score = result_normal.get('final_verdict', {}).get('suspicion_score', 0)
        corrupted_score = result_corrupted.get('final_verdict', {}).get('suspicion_score', 0)
        
        print(f"   Video normal: {normal_score:.3f}")
        print(f"   Video corupt: {corrupted_score:.3f}")
        print(f"   Diferență: {corrupted_score - normal_score:.3f}")
        
        if corrupted_score > normal_score:
            print("✅ Sistemul detectează corect diferențele!")
        else:
            print("⚠️  Sistemul nu detectează diferențe semnificative")
        
    except Exception as e:
        print(f"❌ Eroare la analiza video corupt: {e}")
    
    # Cleanup
    analyzer.cleanup()
    
    try:
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Fișiere temporare șterse din {temp_dir}")
    except:
        print(f"⚠️  Nu s-au putut șterge fișierele din {temp_dir}")

def test_individual_components():
    """Testează componentele individuale ale analizorului"""
    
    print("\n🔧 TESTEZ COMPONENTE INDIVIDUALE")
    print("=" * 60)
    
    analyzer = VideoAnalyzer()
    
    # Creează un video mic pentru test
    temp_dir = tempfile.mkdtemp()
    test_video = os.path.join(temp_dir, "test_components.mp4")
    create_test_video(test_video, duration_seconds=2)
    
    try:
        # Test extragere frame-uri
        print("📸 Testez extragerea de frame-uri...")
        frames = analyzer.extract_frames(test_video, max_frames=10)
        print(f"   ✅ Extrase {len(frames)} frame-uri")
        
        if frames:
            # Test detectare artefacte compresie
            print("🔍 Testez detectarea artefactelor...")
            compression_result = analyzer.detect_compression_artifacts(frames)
            print(f"   ✅ Calitate detectată: {compression_result.get('quality_level', 'N/A')}")
            
            # Test inconsistențe temporale
            if len(frames) > 1:
                print("⏱️  Testez inconsistențele temporale...")
                temporal_result = analyzer.detect_temporal_inconsistencies(frames)
                print(f"   ✅ Verdict temporal: {temporal_result.get('temporal_verdict', 'N/A')}")
            
            # Test detectare deepfake
            print("👤 Testez detectarea deepfake...")
            deepfake_result = analyzer.detect_deepfake_indicators(frames)
            print(f"   ✅ Fețe detectate: {deepfake_result.get('total_faces_detected', 0)}")
        
        # Test metadata
        print("📋 Testez extragerea metadata...")
        metadata = analyzer.get_video_metadata(test_video)
        if metadata.get('has_metadata'):
            print("   ✅ Metadata extrase cu succes")
        else:
            print("   ⚠️  Nu s-au putut extrage metadata (ffprobe nu e instalat?)")
    
    except Exception as e:
        print(f"❌ Eroare la testarea componentelor: {e}")
    
    finally:
        analyzer.cleanup()
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except:
            pass

if __name__ == "__main__":
    print("🚀 ÎNCEPE TESTAREA ANALIZORULUI VIDEO")
    test_individual_components()
    test_video_analyzer()
    print("\n🎉 TESTARE COMPLETĂ!") 