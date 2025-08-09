import pandas as pd
import os
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict, Any
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import db_manager
from utils.logger import log_system_event
from utils.helpers import format_datetime, ensure_directory_exists

class ReportGenerator:
    def __init__(self, output_directory: str = "reports"):
        self.output_directory = output_directory
        ensure_directory_exists(output_directory)
    
    def generate_daily_attendance_report(self, report_date: str, class_id: int = None, 
                                       format: str = 'excel') -> Optional[str]:
        """
        Tạo báo cáo điểm danh theo ngày
        Args:
            report_date: Ngày báo cáo (YYYY-MM-DD)
            class_id: ID lớp học (None để lấy tất cả)
            format: 'excel' hoặc 'pdf'
        Returns:
            Đường dẫn file báo cáo
        """
        try:
        
            attendance_data = db_manager.get_attendance_records(
                class_id=class_id,
                date_from=report_date,
                date_to=report_date
            )
            
            if not attendance_data:
                log_system_event("REPORT", f"Không có dữ liệu điểm danh cho ngày {report_date}")
                return None
            

            df = pd.DataFrame(attendance_data)
            
    
            date_str = report_date.replace('-', '')
            class_suffix = f"_class{class_id}" if class_id else "_all"
            filename = f"daily_attendance_{date_str}{class_suffix}.{format.lower()}"
            filepath = os.path.join(self.output_directory, filename)
            
            if format.lower() == 'excel':
                return self._create_excel_report(df, filepath, f"Báo cáo điểm danh ngày {report_date}")
            elif format.lower() == 'pdf':
                return self._create_pdf_report(df, filepath, f"Báo cáo điểm danh ngày {report_date}")
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo báo cáo điểm danh hàng ngày: {e}")
            return None
    
    def generate_weekly_attendance_report(self, start_date: str, class_id: int = None,
                                        format: str = 'excel') -> Optional[str]:
        """
        Tạo báo cáo điểm danh theo tuần
        Args:
            start_date: Ngày bắt đầu tuần (YYYY-MM-DD)
            class_id: ID lớp học (None để lấy tất cả)
            format: 'excel' hoặc 'pdf'
        Returns:
            Đường dẫn file báo cáo
        """
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = start_date_obj + timedelta(days=6)
            end_date = end_date_obj.strftime("%Y-%m-%d")
            
          
            attendance_data = db_manager.get_attendance_records(
                class_id=class_id,
                date_from=start_date,
                date_to=end_date
            )
            
            if not attendance_data:
                log_system_event("REPORT", f"Không có dữ liệu điểm danh cho tuần {start_date} - {end_date}")
                return None
            
           
            df = pd.DataFrame(attendance_data)
            
           
            pivot_df = df.pivot_table(
                index=['user_name', 'student_id'], 
                columns='attendance_date', 
                values='status',
                fill_value='Absent',
                aggfunc='first'
            )
            
          
            pivot_df = pivot_df.reset_index()
            
            
            week_str = f"{start_date.replace('-', '')}_to_{end_date.replace('-', '')}"
            class_suffix = f"_class{class_id}" if class_id else "_all"
            filename = f"weekly_attendance_{week_str}{class_suffix}.{format.lower()}"
            filepath = os.path.join(self.output_directory, filename)
            
            if format.lower() == 'excel':
                return self._create_excel_pivot_report(pivot_df, filepath, 
                                                     f"Báo cáo điểm danh tuần {start_date} - {end_date}")
            elif format.lower() == 'pdf':
                return self._create_pdf_report(pivot_df, filepath, 
                                             f"Báo cáo điểm danh tuần {start_date} - {end_date}")
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo báo cáo điểm danh hàng tuần: {e}")
            return None
    
    def generate_monthly_attendance_report(self, year: int, month: int, class_id: int = None,
                                         format: str = 'excel') -> Optional[str]:
        """
        Tạo báo cáo điểm danh theo tháng
        """
        try:
            start_date = f"{year}-{month:02d}-01"
            
            if month == 12:
                next_month = f"{year+1}-01-01"
            else:
                next_month = f"{year}-{month+1:02d}-01"
            
            end_date_obj = datetime.strptime(next_month, "%Y-%m-%d").date() - timedelta(days=1)
            end_date = end_date_obj.strftime("%Y-%m-%d")
            
            attendance_data = db_manager.get_attendance_records(
                class_id=class_id,
                date_from=start_date,
                date_to=end_date
            )
            
            if not attendance_data:
                log_system_event("REPORT", f"Không có dữ liệu điểm danh cho tháng {month}/{year}")
                return None
            
            df = pd.DataFrame(attendance_data)
            
            summary_stats = self._calculate_monthly_statistics(df)
            
        
            filename = f"monthly_attendance_{year}{month:02d}.{format.lower()}"
            filepath = os.path.join(self.output_directory, filename)
            
            if format.lower() == 'excel':
                return self._create_monthly_excel_report(df, summary_stats, filepath, 
                                                       f"Báo cáo điểm danh tháng {month}/{year}")
            elif format.lower() == 'pdf':
                return self._create_monthly_pdf_report(df, summary_stats, filepath, 
                                                     f"Báo cáo điểm danh tháng {month}/{year}")
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo báo cáo điểm danh hàng tháng: {e}")
            return None
    
    def generate_student_attendance_summary(self, student_id: int, 
                                          date_from: str = None, date_to: str = None,
                                          format: str = 'excel') -> Optional[str]:
        """
        Tạo báo cáo tổng hợp điểm danh của một sinh viên
        """
        try:

            student_info = db_manager.get_user_by_id(student_id)
            if not student_info:
                log_system_event("ERROR", f"Không tìm thấy sinh viên ID: {student_id}")
                return None
            

            attendance_data = db_manager.get_attendance_records(
                user_id=student_id,
                date_from=date_from,
                date_to=date_to
            )
            
            if not attendance_data:
                log_system_event("REPORT", f"Không có dữ liệu điểm danh cho sinh viên {student_info['name']}")
                return None
            
            df = pd.DataFrame(attendance_data)
            

            student_name = student_info['name'].replace(' ', '_')
            period_str = ""
            if date_from and date_to:
                period_str = f"_{date_from.replace('-', '')}_to_{date_to.replace('-', '')}"
            
            filename = f"student_summary_{student_name}{period_str}.{format.lower()}"
            filepath = os.path.join(self.output_directory, filename)
            
            if format.lower() == 'excel':
                return self._create_student_excel_report(df, student_info, filepath)
            elif format.lower() == 'pdf':
                return self._create_student_pdf_report(df, student_info, filepath)
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo báo cáo sinh viên: {e}")
            return None
    
    def generate_class_statistics_report(self, class_id: int, date_from: str = None, 
                                       date_to: str = None, format: str = 'excel') -> Optional[str]:
        """
        Tạo báo cáo thống kê lớp học
        """
        try:

            class_info = db_manager.get_class_by_id(class_id)
            if not class_info:
                log_system_event("ERROR", f"Không tìm thấy lớp ID: {class_id}")
                return None

            attendance_data = db_manager.get_attendance_records(
                class_id=class_id,
                date_from=date_from,
                date_to=date_to
            )
            

            students_in_class = db_manager.get_students_in_class(class_id)

            stats = self._calculate_class_statistics(attendance_data, students_in_class, date_from, date_to)
            

            class_name = class_info['class_name'].replace(' ', '_')
            period_str = ""
            if date_from and date_to:
                period_str = f"_{date_from.replace('-', '')}_to_{date_to.replace('-', '')}"
            
            filename = f"class_stats_{class_name}{period_str}.{format.lower()}"
            filepath = os.path.join(self.output_directory, filename)
            
            if format.lower() == 'excel':
                return self._create_class_stats_excel_report(stats, class_info, filepath)
            elif format.lower() == 'pdf':
                return self._create_class_stats_pdf_report(stats, class_info, filepath)
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo báo cáo thống kê lớp: {e}")
            return None
    
    def _create_excel_report(self, df: pd.DataFrame, filepath: str, title: str) -> str:
        """Tạo báo cáo Excel cơ bản"""
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
               
                df.to_excel(writer, sheet_name='Attendance Data', index=False)
                
               
                workbook = writer.book
                worksheet = writer.sheets['Attendance Data']
                
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
              
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
              
                for i, col in enumerate(df.columns):
                    column_len = max(df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)
                
                
                title_format = workbook.add_format({'bold': True, 'font_size': 16})
                worksheet.insert_row(0)
                worksheet.write(0, 0, title, title_format)
                
            log_system_event("REPORT", f"Đã tạo báo cáo Excel: {filepath}")
            return filepath
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo Excel report: {e}")
            return None
    
    def _create_excel_pivot_report(self, pivot_df: pd.DataFrame, filepath: str, title: str) -> str:
        """Tạo báo cáo Excel với pivot table"""
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                
                pivot_df.to_excel(writer, sheet_name='Pivot Table', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['Pivot Table']
                
                
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
              
                present_format = workbook.add_format({'fg_color': '#C6EFCE'})  
                absent_format = workbook.add_format({'fg_color': '#FFC7CE'})   
                
            
                for col_num, value in enumerate(pivot_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                
                for row in range(1, len(pivot_df) + 1):
                    for col in range(2, len(pivot_df.columns)):  
                        cell_value = worksheet.read(row, col)
                        if cell_value == 'Present':
                            worksheet.write(row, col, cell_value, present_format)
                        elif cell_value == 'Absent':
                            worksheet.write(row, col, cell_value, absent_format)
                

                for i, col in enumerate(pivot_df.columns):
                    column_len = max(pivot_df[col].astype(str).str.len().max(), len(col)) + 2
                    worksheet.set_column(i, i, column_len)
  
                title_format = workbook.add_format({'bold': True, 'font_size': 16})
                worksheet.insert_row(0)
                worksheet.write(0, 0, title, title_format)
                
            log_system_event("REPORT", f"Đã tạo báo cáo Excel pivot: {filepath}")
            return filepath
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo Excel pivot report: {e}")
            return None
    
    def _create_pdf_report(self, df: pd.DataFrame, filepath: str, title: str) -> str:
        """Tạo báo cáo PDF"""
        try:
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            elements = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  
            )
            
            # Add title
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))
            
            # Convert DataFrame to list of lists
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Create table
            table = Table(data, repeatRows=1)
            
            # Table style
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            
            log_system_event("REPORT", f"Đã tạo báo cáo PDF: {filepath}")
            return filepath
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo PDF report: {e}")
            return None
    
    def _calculate_monthly_statistics(self, df: pd.DataFrame) -> Dict:
        """Tính toán thống kê tháng"""
        stats = {
            'total_records': len(df),
            'unique_students': df['user_name'].nunique(),
            'unique_classes': df['class_name'].nunique(),
            'attendance_by_status': df['status'].value_counts().to_dict(),
            'daily_attendance': df.groupby('attendance_date').size().to_dict(),
            'top_attendees': df['user_name'].value_counts().head(10).to_dict()
        }
        return stats
    
    def _calculate_class_statistics(self, attendance_data: List[Dict], 
                                  students_in_class: List[Dict],
                                  date_from: str = None, date_to: str = None) -> Dict:
        """Tính toán thống kê lớp học"""
        df = pd.DataFrame(attendance_data) if attendance_data else pd.DataFrame()
        
        total_students = len(students_in_class)
        total_sessions = 0
        attendance_rate = 0.0
        
        if not df.empty:
            total_sessions = df['attendance_date'].nunique()
            total_present = len(df[df['status'] == 'Present'])
            total_possible = total_students * total_sessions
            attendance_rate = (total_present / total_possible * 100) if total_possible > 0 else 0.0
        
        stats = {
            'total_students': total_students,
            'total_sessions': total_sessions,
            'attendance_rate': attendance_rate,
            'students_list': students_in_class,
            'attendance_data': attendance_data,
            'date_range': f"{date_from} to {date_to}" if date_from and date_to else "All time"
        }
        
        return stats
    
    def _create_monthly_excel_report(self, df: pd.DataFrame, stats: Dict, 
                                   filepath: str, title: str) -> str:
        """Tạo báo cáo Excel tháng với thống kê"""
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                # Raw data sheet
                df.to_excel(writer, sheet_name='Raw Data', index=False)
                
                # Statistics sheet
                stats_data = []
                for key, value in stats.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            stats_data.append([f"{key}_{sub_key}", sub_value])
                    else:
                        stats_data.append([key, value])
                
                stats_df = pd.DataFrame(stats_data, columns=['Metric', 'Value'])
                stats_df.to_excel(writer, sheet_name='Statistics', index=False)
                
                workbook = writer.book
                
                # Format both sheets
                for sheet_name in ['Raw Data', 'Statistics']:
                    worksheet = writer.sheets[sheet_name]
                    
                    # Header format
                    header_format = workbook.add_format({
                        'bold': True,
                        'fg_color': '#D7E4BC',
                        'border': 1
                    })
                    
                    # Apply header format
                    for col in range(len(worksheet.get_worksheet().dim_colmax or 0) + 1):
                        worksheet.write(0, col, worksheet.read(0, col), header_format)
                
            log_system_event("REPORT", f"Đã tạo báo cáo Excel tháng: {filepath}")
            return filepath
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo monthly Excel report: {e}")
            return None
    
    def _create_student_excel_report(self, df: pd.DataFrame, student_info: Dict, filepath: str) -> str:
        """Tạo báo cáo Excel cho sinh viên"""
        try:
            with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
                # Student info sheet
                info_data = [
                    ['Tên', student_info['name']],
                    ['Mã SV', student_info['student_id']],
                    ['Vai trò', student_info['role']],
                    ['Tổng số buổi điểm danh', len(df)],
                    ['Số buổi có mặt', len(df[df['status'] == 'Present'])],
                    ['Tỷ lệ điểm danh (%)', len(df[df['status'] == 'Present']) / len(df) * 100 if len(df) > 0 else 0]
                ]
                
                info_df = pd.DataFrame(info_data, columns=['Thông tin', 'Giá trị'])
                info_df.to_excel(writer, sheet_name='Student Info', index=False)
                
                # Attendance records
                df.to_excel(writer, sheet_name='Attendance Records', index=False)
                
            log_system_event("REPORT", f"Đã tạo báo cáo sinh viên: {filepath}")
            return filepath
            
        except Exception as e:
            log_system_event("ERROR", f"Lỗi tạo student Excel report: {e}")
            return None
    
    def get_available_reports(self) -> List[Dict]:
        """Lấy danh sách các báo cáo có sẵn"""
        reports = []
        try:
            for filename in os.listdir(self.output_directory):
                if filename.endswith(('.xlsx', '.pdf')):
                    filepath = os.path.join(self.output_directory, filename)
                    file_stats = os.stat(filepath)
                    
                    reports.append({
                        'filename': filename,
                        'filepath': filepath,
                        'size': file_stats.st_size,
                        'created_time': datetime.fromtimestamp(file_stats.st_ctime),
                        'modified_time': datetime.fromtimestamp(file_stats.st_mtime)
                    })
        except Exception as e:
            log_system_event("ERROR", f"Lỗi lấy danh sách reports: {e}")
        
        return sorted(reports, key=lambda x: x['modified_time'], reverse=True)
    
    def cleanup_old_reports(self, days_old: int = 30) -> int:
        """Xóa các báo cáo cũ"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        deleted_count = 0
        
        try:
            for filename in os.listdir(self.output_directory):
                if filename.endswith(('.xlsx', '.pdf')):
                    filepath = os.path.join(self.output_directory, filename)
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        log_system_event("CLEANUP", f"Đã xóa báo cáo cũ: {filename}")
        
        except Exception as e:
            log_system_event("ERROR", f"Lỗi cleanup reports: {e}")
        
        return deleted_count

# Singleton instance
report_generator = ReportGenerator()