# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    def _account_entry_move(self):
        if self.product_id.type in ["consu"] and self.product_id.journal_on_move:
            location_from = self.location_id
            location_to = self.location_dest_id
            company_from = self.mapped("move_line_ids.location_id.company_id") if self._is_out() else False
            company_to = self.mapped("move_line_ids.location_dest_id.company_id") if self._is_in() else False

            if self._is_in():
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
                if location_from and location_from.usage == "customer":  # goods returned from customer
                    self.with_context(force_company=company_to.id)._create_account_move_line(acc_dest, acc_valuation, journal_id)
                else:
                    self.with_context(force_company=company_to.id)._create_account_move_line(acc_src, acc_valuation, journal_id)

            # Create Journal Entry for products leaving the company
            if self._is_out():
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
                if location_to and location_to.usage == "supplier":  # goods returned to supplier
                    self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_src, journal_id)
                else:
                    self.with_context(force_company=company_from.id)._create_account_move_line(acc_valuation, acc_dest, journal_id)

            if self.company_id.anglo_saxon_accounting:
                # Creates an account entry from stock_input to stock_output on a dropship move. https://github.com/odoo/odoo/issues/12687
                journal_id, acc_src, acc_dest, acc_valuation = self._get_accounting_data_for_valuation()
                if self._is_dropshipped():
                    self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_src, acc_dest, journal_id)
                elif self._is_dropshipped_returned():
                    self.with_context(force_company=self.company_id.id)._create_account_move_line(acc_dest, acc_src, journal_id)
        return super(StockMove, self)._account_entry_move()
